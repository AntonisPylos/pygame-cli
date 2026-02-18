from .path import get_path, valid_project, create_path

import json
import shutil
import getpass
import venv
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List, Optional

from git import Repo


def _prompt(prompt: str, default: Optional[str] = None) -> str:
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def _normalize_tags(tags: Any) -> List[str]:
    if tags is None:
        return []
    if isinstance(tags, str):
        parts = tags.split(",")
    elif isinstance(tags, Iterable):
        parts = list(tags)
    else:
        return []
    return [p.strip() for p in parts if p and p.strip()]


def new_project(args: Any) -> str:
    """Create a new project.

    Expects:
        - args.name (str): Name of the new project.
        - args.description (str, optional): Optional project description.
        - args.author (str, optional): Project author or studio name.
        - args.tags (str, optional): List of project tags.
        - args.input (bool, optional): Whether to prompt for project data via terminal input.
    """
    if not hasattr(args, "name") or not args.name:
        raise ValueError("args.name is required")

    name = args.name

    path = Path(get_path(name))
    if valid_project(name):
        print(f"Project `{name}` already exists")
        return None

    system_user = getpass.getuser()
    author = getattr(args, "author", None) or system_user
    description = getattr(args, "description", " ") or ""
    version = getattr(args, "version", "") or "0.0.0"
    tags = _normalize_tags(getattr(args, "tags", None))

    if getattr(args, "input", False):
        print("Note: to accept the default value shown in brackets, just press Enter")
        print("===============================================================")
        author_in = _prompt("Enter project author", default=author)
        desc_in = _prompt("Enter project description", default=description)
        ver_in = _prompt("Enter project version", default=version)
        tags_in = _prompt(
            "Enter project tags (comma separated)",
            default=",".join(tags) if tags else "",
        )
        if author_in:
            author = author_in
        if desc_in:
            description = desc_in
        if ver_in:
            version = ver_in
        if tags_in:
            tags = _normalize_tags(tags_in)
        print("===============================================================")

    tags = list(tags)

    full_path = Path(create_path(name))

    venv_dir = full_path / ".env"
    try:
        metadata = {
            "name": name,
            "description": description,
            "author": author,
            "version": version,
            "tags": tags,
            "created": datetime.today().strftime("%d/%m/%Y"),
        }

        metadata_file = full_path / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        # create virtual environment in .env (with pip)
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(str(venv_dir))

        # Simple template copy
        template_src = Path(__file__).parent.parent / "template"
        shutil.copytree(str(template_src), str(full_path), dirs_exist_ok=True)

        # create .git
        repo = Repo.init(str(full_path))
        repo.git.add(A=True)
        repo.index.commit(f"init")
        repo.git.branch("-M", "main")

        print(f"Path: {full_path}")
        print(f"Project '{name}' created successfully!")
        return str(full_path)

    except Exception:
        shutil.rmtree(full_path)
        raise
