from .path import get_path, valid_project

import json
from pathlib import Path
from typing import Any, Optional


def info_project(args: Any) -> Optional[dict]:
    """Display project metadata.

    Expects:
      - args.name (str): project name
    """
    if not hasattr(args, "name") or not args.name:
        raise ValueError("args.name is required")

    name = args.name
    project_path = Path(get_path(name))

    if not valid_project(name):
        print(f"No project found with name '{name}'")
        return None

    metadata_file = project_path / "metadata.json"

    try:
        with metadata_file.open("r", encoding="utf-8") as f:
            metadata = json.load(f)
    except json.JSONDecodeError:
        print("Error: Failed to parse metadata.json. Is it valid JSON?")
        return None
    except Exception as exc:
        print(f"Failed to read metadata for '{name}': {exc}")
        return None

    tags = metadata.get("tags") or []
    if not isinstance(tags, (list, tuple)):
        # tolerate a comma-separated string
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        else:
            tags = []

    print("=======================")
    print(f"Name:        {metadata.get('name')}")
    print(f"Description: {metadata.get('description')}")
    print(f"Version:     {metadata.get('version')}")
    print(f"Tags:        {', '.join(tags) if tags else ''}")
    print("=======================")
    print(f"Author:      {metadata.get('author')}")
    print(f"Created:     {metadata.get('created')}")
    print("=======================")

    return metadata
