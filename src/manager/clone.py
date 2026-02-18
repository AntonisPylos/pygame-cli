from .path import valid_project, create_path

import shutil
import venv
from pathlib import Path
from typing import Any, Optional

from git import Repo

def clone_project(args: Any) -> Optional[str]:
    """Clone a Git repository as a new project.

    Expects:
        - source (str): Git repository URL HTTPS/SSH
    """
    if not hasattr(args, "source") or not args.source:
        raise ValueError("args.source is required")

    source = args.source
    name = source.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]

    if valid_project(name):
        print(f"Project `{name}` already exists")
        return None

    full_path = Path(create_path(name))

    try:
        print(f"Cloning from {source} ...")
        Repo.clone_from(source, str(full_path))
        venv_dir = full_path / ".env"
        print("Creating virtual environment...")
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(str(venv_dir))

        if not valid_project(name):
            print(f"{name} is not a valid project")
            shutil.rmtree(full_path)
            return None

        print(f"Path: {full_path}")
        print(f"Project '{name}' cloned successfully!")
        return str(full_path)

    except Exception:
        shutil.rmtree(full_path)
        raise
