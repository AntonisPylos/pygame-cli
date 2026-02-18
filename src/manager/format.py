from .path import get_projects_path

from random import randint as random
from shutil import rmtree as rm
from typing import Any, Optional


def format_projects(args: Any) -> Optional[str]:
    """Format the project directory by removing all projects.

    Expects:
      - args.force (bool, optional): to skip confirmation and timer
    """
    force = args.force
    path = get_projects_path()

    if not force:
        print("WARNING: This action will permanently delete ALL projects!")
        secure_number = str(random(1000, 9999))
        answer = input(f"To confirm, please type the number {secure_number}: ").strip()

        if answer != secure_number:
            print("!!!Wrong Answer!!!")
            print("No action taken")
            return None

    try:
        rm(path)
    except Exception as exc:
        print(f"Failed to delete project '{name}': {exc}")
        return None

    print("All projects deleted successfully!")
    return path
