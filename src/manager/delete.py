from .path import get_path, valid_project

import shutil
import time
from pathlib import Path
from typing import Any, Optional


def delete_project(args: Any) -> Optional[str]:
    """Delete a project

    Expects:
      - args.name (str): project name
      - args.force (bool, optional): to skip confirmation and timer
    """
    if not hasattr(args, "name") or not args.name:
        raise ValueError("args.name is required")

    name = args.name
    force = args.force

    path = Path(get_path(name))
    if not valid_project(name):
        print(f"No project found with name '{name}'")
        return None

    timer = 3
    if not force:
        print("WARNING: This action is irreversible")
        try:
            confirm = (
                input(f"Are you sure you want to delete project '{name}'? [y/N] ")
                .strip()
                .lower()
            )
            if confirm != "y":
                print("No action taken")
                return None
        except (EOFError, KeyboardInterrupt):
            print("No action taken")
            return None

        while timer > 0:
            print(f"Deleting in {timer} second{'s' if timer != 1 else ''}...")
            time.sleep(1)
            timer -= 1

    try:
        shutil.rmtree(path)
    except Exception as exc:
        print(f"Failed to delete project '{name}': {exc}")
        return None

    print(f"project `{name}` deleted successfully!")
    return str(path)
