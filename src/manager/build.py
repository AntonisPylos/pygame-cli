from .info import info_project as info
from .path import get_path, valid_project

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import urllib.request
from time import perf_counter as time
from typing import Any


def _parse_package_names(requirements: str) -> list[str]:
    includes = [
        dep.split("==")[0]
        .split(">=")[0]
        .split(">")[0]
        .split("<")[0]
        .split("[")[0]
        .strip()
        .replace("-", "_")
        for dep in requirements.splitlines()
        if dep.strip() and not dep.strip().startswith("#")
    ]
    return includes


def _get_installed_version(
    venv_site_packages: str, package_name: str, pypi_name: str
) -> str:
    # Temporarily add the venv site-packages to sys.path
    original_path = sys.path.copy()
    sys.path.insert(0, venv_site_packages)

    from importlib.metadata import version, PackageNotFoundError

    # Try different naming conventions
    possible_names = [package_name, pypi_name, pypi_name.replace("-", "_")]

    for name in possible_names:
        try:
            return version(name)
        except (PackageNotFoundError, Exception):
            continue
        return None

    # Return sys.path back to normal
    sys.path = original_path


def _collect_licenses(
    venv_site_packages: str, build_dir: str, includes: list[str], output: str
) -> int:
    os.makedirs(output, exist_ok=True)

    licenses_collected = 0

    print(f"\tFetching license info for {len(includes)} dependencies...")

    for package_name in includes:
        # Try different name variations
        pypi_name = package_name.replace("_", "-")
        installed_version = _get_installed_version(
            venv_site_packages, package_name, pypi_name
        )

        if not installed_version:
            print(f"\t! Warning: Could not determine version for {pypi_name}")
            installed_version = "unknown"

        if installed_version != "unknown":
            pypi_url = f"https://pypi.org/pypi/{pypi_name}/{installed_version}/json"
        else:
            pypi_url = f"https://pypi.org/pypi/{pypi_name}/json"

        try:
            with urllib.request.urlopen(pypi_url, timeout=5) as response:
                data = json.loads(response.read().decode())

                # Get metadata
                info_data = data.get("info", {})
                license_text = info_data.get("license", "Not specified")
                author = info_data.get("author", "Unknown")
                version = info_data.get("version", installed_version)
                home_page = info_data.get("home_page", "")
                project_url = info_data.get(
                    "project_url", f"https://pypi.org/project/{pypi_name}/{version}/"
                )

                # Get classifiers for additional license info
                classifiers = info_data.get("classifiers", [])
                license_classifiers = [
                    c for c in classifiers if c.startswith("License ::  ")
                ]

                # Create license file with version in filename
                license_file_path = os.path.join(
                    output, f"{pypi_name}_{version}_LICENSE.txt"
                )

                if not license_text or license_text == "Not specified":
                    print(f"\t! Warning: Could not determine the {pypi_name} license")

                with open(license_file_path, "w", encoding="utf-8") as f:
                    f.write(f"Package: {pypi_name}\n")
                    f.write(f"Version: {version}\n")
                    f.write(f"Author: {author}\n")
                    if home_page:
                        f.write(f"Site: {home_page}\n")
                    f.write("=" * 70 + "\n\n")

                    if license_text and license_text != "Not specified":
                        f.write(f"License: {license_text}\n\n")

                    if license_classifiers:
                        f.write("License Classifiers:\n")
                        for classifier in license_classifiers:
                            f.write(f"  - {classifier}\n")
                        f.write("\n")

                    f.write("-" * 70 + "\n")
                    f.write("For the full license text, please visit:\n")
                    f.write(f"{project_url}\n")

                licenses_collected += 1

        except urllib.error.HTTPError as e:
            print(f"\t! Warning: HTTP {e.code} for {pypi_name} (v{installed_version})")
        except Exception as e:
            print(
                f"\t! Warning: Failed to fetch license for {pypi_name}: {str(e)[:50]}"
            )

    # Create a small README
    readme_path = os.path.join(output, "README.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("THIRD-PARTY LICENSES\n")
        f.write("=" * 70 + "\n\n")
        f.write("This directory contains license information for all third-party\n")
        f.write("libraries included in this application.\n\n")
        f.write("All license information was retrieved from PyPI.\n\n")
        f.write("=" * 70 + "\n\n")

    return licenses_collected


def local_build(args):
    """Build a local executable using cx_Freeze.

    Expects:
        - args.name (str): project name
    """
    x1 = time()
    name = args.name

    if not valid_project(name):
        print(f"✗ No project found with name '{name}'")
        return

    project_path = get_path(name)
    main_script = os.path.join(project_path, "main.py")

    print("BUILD METADATA")

    metadata = info(args)
    app_name = metadata["name"]
    if not app_name:
        app_name = "Game"
    app_version = metadata["version"]
    if not app_version:
        app_version = "1.0.0"

    build_dir = os.path.abspath("build")

    # Determine executable type
    if sys.platform == "win32":
        base = "'gui'"
        target_name = f"{app_name}.exe"
    else:
        base = "None"
        target_name = app_name

    # Parse requirements
    req_file = os.path.join(project_path, "requirements.txt")

    with open(req_file, "r") as req:
        requirements = req.read()

    includes = _parse_package_names(requirements)

    # Replace pygame_ce with pygame for cx_Freeze
    includes.remove("pygame_ce")
    includes.append("pygame")
    if "pygbag" in includes:
        includes.remove("pygbag")

    env_folder = os.path.join(project_path, ".env")

    # Find site-packages in the virtual environment
    if sys.platform == "win32":
        venv_site_packages = os.path.join(env_folder, "Lib", "site-packages")
    else:
        lib_dir = os.path.join(env_folder, "lib")
        if os.path.exists(lib_dir):
            python_dirs = [d for d in os.listdir(lib_dir) if d.startswith("python")]
            if python_dirs:
                venv_site_packages = os.path.join(
                    lib_dir, python_dirs[0], "site-packages"
                )
            else:
                venv_site_packages = None
        else:
            venv_site_packages = None

    # Check if virtual environment exists
    if not venv_site_packages or not os.path.exists(venv_site_packages):
        print(f"\t✗ Virtual environment not found at:  {env_folder}")
        print(f"\t! Expected site-packages at: {venv_site_packages}")
        return

    print(f"Platform:    {sys.platform}")
    print("=======================")

    # Remove previous build
    if os.path.exists(build_dir):
        print(f"[1/5] Cleaning previous build...")
        try:
            shutil.rmtree(build_dir)
            print(f"\t✓ Removed:  {build_dir}")
        except Exception as e:
            print(f"\t✗ Error:  {e}")
            return
    else:
        print(f"[1/5] No previous build found")

    os.makedirs(build_dir, exist_ok=True)

    if not os.path.exists(os.path.join(project_path, "__pycache__")):
        print(
            "✗ Error: No __pycache__ found. Please run the game at least once to generate cache files"
        )
        return

    print(f"[2/5] Running cx_Freeze...")

    # Find project modules and packages
    project_packages = []  # Directories with __init__.py
    project_modules = []  # .py files

    for item in os.listdir(project_path):
        item_path = os.path.join(project_path, item)
        if os.path.isdir(item_path) and not item.startswith("."):
            init_file = os.path.join(item_path, "__init__.py")
            if os.path.exists(init_file):
                project_packages.append(item)

        elif item.endswith(".py") and item != "main.py":
            project_modules.append(item[:-3])  # Remove .py extension

    print(f"\tFound {len(includes)} dependencies: {includes}")
    print(f"\tFound {len(project_packages)} packages: {project_packages}")
    print(f"\tFound {len(project_modules)} modules: {project_modules}")

    # Generate cx_Freeze setup script
    setup_code = textwrap.dedent(f"""\
        import sys
        from cx_Freeze import setup, Executable

        # Add virtual environment site-packages to sys.path
        sys.path.insert(0, r"{venv_site_packages}")
        # Add project path
        sys.path.insert(0, r"{project_path}")

        # Packages (directories with __init__.py)
        packages = {project_packages!r}

        # Standalone modules (.py files)
        modules = {project_modules!r}

        # External packages from requirements.txt
        external_packages = {includes!r}

        setup(
            name="{app_name}",
            version="{app_version}",
            description="{app_name} Build",
            executables=[Executable(r"{main_script}", target_name="{target_name}", base={base})],
            options={{
                "build_exe": {{
                    "build_exe": r"{build_dir}",
                    "packages": packages + external_packages,
                    "includes": modules,  # Standalone modules go here
                    "include_files": [],
                    "path": [r"{venv_site_packages}", r"{project_path}"] + sys.path,
                }}
            }}
        )
        """)

    # Create temp script file for cx_freeze
    with tempfile.TemporaryDirectory() as temp_dir:
        setup_script_path = os.path.join(temp_dir, "setup_cxfreeze.py")
        with open(setup_script_path, "w") as f:
            f.write(setup_code)

        try:
            # Run cx_Freeze using system Python (which has cx_Freeze installed)
            # but with the venv site-packages in PYTHONPATH
            env = os.environ.copy()
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = (
                    f"{venv_site_packages}{os.pathsep}{env['PYTHONPATH']}"
                )
            else:
                env["PYTHONPATH"] = venv_site_packages

            result = subprocess.run(
                [sys.executable, setup_script_path, "build"],
                check=True,
                cwd=temp_dir,
                env=env,
                stdout=subprocess.DEVNULL,
                # stderr=subprocess.DEVNULL,
            )
            print(f"\t✓ cx_Freeze completed")
        except subprocess.CalledProcessError as e:
            print(f"\t✗ cx_Freeze failed (exit code {e.returncode})")
            if e.stderr:
                error_msg = e.stderr.decode()
                print(f"\tError output:")
                for line in error_msg.splitlines()[:10]:
                    print(f"\t  {line}")
            if e.stdout:
                print(f"\tstdout: {e.stdout.decode()}")
            return

    print(f"[3/5] Copying project assets...")


    # Data folders
    whitelist = {
        "assets", "data"
    }

    copied_count = 0

    for item in os.listdir(project_path):
        src = os.path.join(project_path, item)
        dst = os.path.join(build_dir, item)

        if os.path.isdir(src) and item.lower() in whitelist:
            try:
                shutil.copytree(src, dst)
                print(f"\t✓ Moved {item}/")
                copied_count += 1
            except Exception as e:
                print(f"\t✗ Failed to move {item}/: {e}")

    print(f"Total files moved: {copied_count}")

    if copied_count == 0:
        print(f"\t!  No assets folder found")

    print(f"[4/5] Collecting licenses...")

    includes.remove("pygame")
    includes.append("pygame_ce")

    licenses_dir = os.path.join(build_dir, "lib", "licenses")
    licenses_count = _collect_licenses(
        venv_site_packages, build_dir, includes, licenses_dir
    )

    if licenses_count > 0:
        print(f"\t✓ Collected {licenses_count + 1} license files")
        print(f"\t→ Location: {licenses_dir}")
    else:
        print(f"\t! No license files found")

    shutil.move(os.path.join(build_dir, "frozen_application_license.txt"), licenses_dir)

    x2 = time()
    build_time = x2 - x1

    print(f"[5/5] Finalizing...")
    print(f"\t✓ BUILD COMPLETED in {build_time:.2f}s")
    print(f"Output: {build_dir}")


def web_build(args):
    """Build a web version using pygbag.

    Expects:
        - args.name (str): project name
    """
    x1 = time()
    name = args.name
    cdn = args.cdn
    template = args.template

    if not valid_project(name):
        print(f"✗ No project found with name '{name}'")
        return

    project_path = get_path(name)
    build_dir = os.path.abspath("build")

    # Remove previous build
    if os.path.exists(build_dir):
        print(f"[1/3] Cleaning previous build...")
        try:
            shutil.rmtree(build_dir)
            print(f"\t✓ Removed: {build_dir}")
        except Exception as e:
            print(f"\t✗ Error: {e}")
            return
    else:
        print(f"[1/3] No previous build found")

    os.makedirs(build_dir, exist_ok=True)

    print(f"[2/3] Running pygbag...")

    cmd = [sys.executable, "-m", "pygbag", "--archive"]
    if cdn is not None:
        cmd.extend(["--cdn", str(cdn)])
    if template is not None:
        cmd.extend(["--template", str(template)])
    cmd.append("main.py")

    env_folder = os.path.join(project_path, ".env")
    if sys.platform == "win32":
        venv_site_packages = os.path.join(env_folder, "Lib", "site-packages")
    else:
        lib_dir = os.path.join(env_folder, "lib")
        if os.path.exists(lib_dir):
            python_dirs = [d for d in os.listdir(lib_dir) if d.startswith("python")]
            if python_dirs:
                venv_site_packages = os.path.join(
                    lib_dir, python_dirs[0], "site-packages"
                )
            else:
                venv_site_packages = None
        else:
            venv_site_packages = None

    env = os.environ.copy()
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = (
            f"{venv_site_packages}{os.pathsep}{env['PYTHONPATH']}"
        )
    else:
        env["PYTHONPATH"] = venv_site_packages

    try:
        subprocess.run(
            cmd,
            check=True,
            env=env,
            cwd=project_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"\t✓ pygbag completed")
    except subprocess.CalledProcessError as e:
        print(f"\t✗ pygbag failed (exit code {e.returncode})")
        return

    # Move build from project to current directory
    pygbag_output_dir = os.path.join(project_path, "build")

    print(f"[3/4] Moving build files...")

    try:
        shutil.rmtree(build_dir)
        shutil.move(pygbag_output_dir, build_dir)
        print(f"\t✓ Files moved to: {build_dir}")
    except Exception as e:
        print(f"\t✗ Failed to move files: {e}")
        try:
            shutil.rmtree(pygbag_output_dir)
        except Exception:
            pass
        return

    print(f"[4/4] Collecting licenses...")

    # Find site-packages in the virtual environment
    env_folder = os.path.join(project_path, ".env")
    if sys.platform == "win32":
        venv_site_packages = os.path.join(env_folder, "Lib", "site-packages")
    else:
        lib_dir = os.path.join(env_folder, "lib")
        if os.path.exists(lib_dir):
            python_dirs = [d for d in os.listdir(lib_dir) if d.startswith("python")]
            if python_dirs:
                venv_site_packages = os.path.join(
                    lib_dir, python_dirs[0], "site-packages"
                )
            else:
                venv_site_packages = None
        else:
            venv_site_packages = None

    # Check if virtual environment exists
    if not venv_site_packages or not os.path.exists(venv_site_packages):
        print(f"\t✗ Virtual environment not found at:  {env_folder}")
        print(f"\t! Expected site-packages at: {venv_site_packages}")
        return

    # Parse requirements
    req_file = os.path.join(project_path, "requirements.txt")

    with open(req_file, "r") as req:
        requirements = req.read()

    includes = _parse_package_names(requirements)
    licenses_dir = os.path.join(build_dir, "licenses")
    licenses_count = _collect_licenses(
        venv_site_packages, build_dir, includes, licenses_dir
    )

    if licenses_count > 0:
        print(f"\t✓ Collected {licenses_count} license files")
        print(f"\t→ Location: {licenses_dir}")
    else:
        print(f"\t! No license files found")

    x2 = time()
    build_time = x2 - x1

    print(f"✓ WEB BUILD COMPLETED in {build_time:.2f}s")
    print(f"Output: {build_dir}")


def build_project(args: Any) -> None:
    """Build a project for local or web.

    Expects:
        - args.name (str): project name
        - args.web (bool, optional): web builds
    """

    if not hasattr(args, "name") or not args.name:
        raise ValueError("args.name is required")
    if args.web:
        web_build(args)
    else:
        local_build(args)
