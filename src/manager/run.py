from .path import get_path, valid_project

import subprocess
import webbrowser
import threading
import shutil
import time
import os
import sys
import venv
from time import perf_counter as time
from time import sleep
from pathlib import Path
from typing import Any, Optional


def _venv_python_path(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"


def _install_requirements_into_venv(venv_dir: Path, req_file: Path) -> None:
    python_exe = _venv_python_path(venv_dir)
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "-r", str(req_file)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _print_program_output(start_time: float, output: str) -> None:
    if not output.strip():
        return
    runtime = time() - start_time
    for line in output.rstrip().splitlines():
        print(f"[{runtime:.2f}] {output}", end="")


def _handle_local_run_error(
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
    stderr: Optional[str] = None,
    title: str = "An unexpected error occurred",
    project_path: Optional[Path] = None,
) -> None:
    if stderr:
        lines = stderr.strip().split("\n")
        for line in reversed(lines):
            if ":" in line and any(
                e in line for e in ["Error", "Exception", "Warning"]
            ):
                parts = line.split(":", 1)
                if not error_type:
                    error_type = parts[0].strip()
                if not error_message:
                    error_message = parts[1].strip() if len(parts) > 1 else ""
                break

        traceback_lines = []
        counter = 1
        for line in lines:
            if line.strip().startswith("File"):
                try:
                    if '"' in line:
                        start = line.index('"') + 1
                        end = line.index('"', start)
                        full_path = line[start:end]

                        if project_path is None or str(project_path) in full_path:
                            filename = os.path.basename(full_path)
                            if "line" in line:
                                line_part = line.split("line")[1].split(",")[0].strip()
                                traceback_lines.append(
                                    f"\t{counter} -> File: {filename} | Line: {line_part}"
                                )
                            else:
                                traceback_lines.append(f"\tFile: {filename}")
                        counter += 1
                except (ValueError, IndexError):
                    pass
        formatted_traceback = (
            "\n" + "\n".join(traceback_lines)
            if traceback_lines
            else " No traceback available"
        )
    else:
        if not error_type:
            error_type = "Unknown"
        if not error_message:
            error_message = "No details provided"
        formatted_traceback = "No traceback available"

    nice_error_message = (
        f"Type: {error_type}\n"
        f"Message: {error_message}\n"
        f"Traceback:{formatted_traceback}"
    )

    print(
        "-----------------------------------\n"
        f"Error: {title}\n"
        f"{nice_error_message}\n"
        "-----------------------------------"
    )


def _open_browser(url: str, delay: float) -> None:
    def delayed_open() -> None:
        sleep(delay)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=delayed_open, daemon=True).start()


def local_run(args: Any) -> None:
    """Run a project locally.

    Expects:
      - args.name (str): project name
    """

    if not hasattr(args, "name") or not args.name:
        raise ValueError("args.name is required")

    name = args.name
    if not valid_project(name):
        print(f"No project found with name '{name}'")
        return

    full_path = Path(get_path(name))
    main_py = full_path / "main.py"
    venv_dir = full_path / ".env"
    req_file = full_path / "requirements.txt"

    try:
        _install_requirements_into_venv(venv_dir, req_file)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        return
    except Exception as e:
        print(f"Error preparing virtualenv: {e}")
        return

    python_exe = _venv_python_path(venv_dir)
    start_time = time()

    try:
        process = subprocess.Popen(
            [str(python_exe), "-u", "main.py"],
            cwd=str(full_path),
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        while True:
            output = process.stdout.readline()
            if output:
                _print_program_output(start_time, output)
            elif process.poll() is not None:
                break

        remaining = process.stdout.read()
        if remaining:
            _print_program_output(start_time, remaining)

        stderr_output = process.stderr.read()
        if process.returncode != 0:
            if stderr_output.strip():
                _handle_local_run_error(
                    stderr=stderr_output,
                    title=f"{name} crashed",
                    project_path=full_path,
                )
            else:
                print(f"ProcessError: Process exited with code {process.returncode}")

    except KeyboardInterrupt:
        print(f"\nProject '{name}' was keyboard interrupted")


def web_run(args: Any, open_delay: int = 10) -> None:
    """Run a project in web mode using pygbag.

    Expects:
      - args.name (str): project name
      - args.cdn (str, optional): CDN option for pygbag
      - args.template (str, optional): template option for pygbag
      - open_delay (int): delay before opening browser
    """
    if not hasattr(args, "name") or not args.name:
        raise ValueError("args.name is required")

    name = args.name
    if not valid_project(name):
        print(f"No project found with name '{name}'")
        return

    cdn = getattr(args, "cdn", None)
    template = getattr(args, "template", None)

    full_path = Path(get_path(name))
    main_py = full_path / "main.py"
    if not main_py.exists():
        print(f"No main.py found in project '{name}' ({main_py})")
        return

    env_folder = os.path.join(full_path, ".env")
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

    url = "http://localhost:8000/"
    try:
        print("Running pygbag ...")
        print(f"Server ready: {url}")
        print("\nPress Ctrl+C to stop the server")
        _open_browser(url, open_delay)

        cmd = [sys.executable, "-m", "pygbag"]
        if cdn is not None:
            cmd.extend(["--cdn", str(cdn)])
        if template is not None:
            cmd.extend(["--template", str(template)])
        cmd.append("main.py")

        subprocess.run(
            cmd,
            check=True,
            cwd=str(full_path),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        print(f"pygbag failed with exit code {e.returncode}")
    except KeyboardInterrupt:
        build_path = full_path / "build"
        if build_path.exists():
            shutil.rmtree(build_path, ignore_errors=True)
        print("\nStopped by user")
    except FileNotFoundError:
        print(
            "pygbag command not found. Please ensure pygbag is installed and available."
        )


def run_project(args: Any) -> None:
    """Run a project.

    Expects:
      - args.name (str): project name
      - args.web (bool): run in web mode if True
    """
    if args.web:
        web_run(args)
    else:
        local_run(args)
