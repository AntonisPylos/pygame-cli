from .path import get_path, valid_project

import subprocess
import sys
from pathlib import Path
from typing import Any, Optional


def explore_projects(args: Any) -> Optional[str]:
    """Open a project folder in the system file browser.

    Expects:
      - args.name (str): project name
    """
    if not hasattr(args, "name") or not args.name:
        raise ValueError("args.name is required")

    name = args.name
    if not valid_project(name):
        print(f"No project found with name '{name}'")
        return None

    project_path = Path(get_path(name))

    # Determine the platform-specific "open folder" command
    if sys.platform.startswith("win"):
        cmd = ["explorer", str(project_path)]
    elif sys.platform == "darwin":
        cmd = ["open", str(project_path)]
    else:
        cmd = ["xdg-open", str(project_path)]

    try:
        subprocess.run(cmd, check=False)
        return str(project_path)
    except Exception as exc:
        print(f"Failed to open project '{name}': {exc}")
        return None
