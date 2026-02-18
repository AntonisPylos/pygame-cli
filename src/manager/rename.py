from .path import get_projects_path, valid_project

import json
import shutil
from pathlib import Path
from typing import Any, Optional


def rename_project(args: Any) -> Optional[str]:
    """Rename a project.

    Expects:
      - args.old_name (str): project old name
      - args.new_name (str): project new name
    """
    if not hasattr(args, "old_name") or not args.old_name:
        raise ValueError("args.old_name is required")

    if not hasattr(args, "new_name") or not args.new_name:
        raise ValueError("args.new_name is required")

    project_root = Path(get_projects_path())
    old_dir = project_root / args.old_name
    new_dir = project_root / args.new_name

    if not valid_project(args.old_name):
        print(f"Project '{args.old_name}' does not exist")
        return None

    if valid_project(args.new_name):
        print(f"A project named '{args.new_name}' already exists")
        return None

    metadata_file = old_dir / "metadata.json"
    try:
        with metadata_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data["name"] = args.new_name
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except json.JSONDecodeError:
        print("Error: Failed to parse metadata.json. Is it valid JSON?")
        return None

    # Move the directory
    try:
        shutil.move(str(old_dir), str(new_dir))
    except Exception as exc:
        print(f"Failed to rename project: {exc}")
        return None

    print(f"Project renamed from '{args.old_name}' to '{args.new_name}'")
    return str(new_dir)
