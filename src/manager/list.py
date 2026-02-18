from .path import get_projects_path, valid_project

from pathlib import Path
from typing import Any, List, Optional


def list_projects(args: Any) -> Optional[str]:
    """List all projects in the projects directory."""

    projects_root = Path(get_projects_path())

    if not projects_root.exists() or not projects_root.is_dir():
        print("No projects found")
        return []

    try:
        projects = [
            p.name
            for p in projects_root.iterdir()
            if p.is_dir() and valid_project(p.name)
        ]
    except Exception as exc:
        print(f"Failed to read projects directory: {exc}")
        return None

    if not projects:
        print("No projects found")
        return []

    projects_sorted = sorted(projects)
    print("Total:", len(projects_sorted))
    print("List:")
    for name in projects_sorted:
        print(f"  - {name}")

    return projects_sorted
