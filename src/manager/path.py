import appdirs

import os
from typing import Any

ORG = "pygame"

def create_path(name: str) -> str:
    """Create/return the path for the target project directory.

    Args:
        name: The project name.

    Returns:
        The absolute path to the project directory.

    Raises:
        ValueError: If the project name is invalid
    """
    _validate_name(name)
    path = os.path.join(get_projects_path(), name)
    os.makedirs(path, exist_ok=True)
    return path


def get_projects_path() -> str:
    """Return the path to the projects directory.

    Creates the directory if it doesn't exist.The location is platform-specific:
        - Linux: ~/.local/share/pygame
        - macOS: ~/Library/Application Support/pygame
        - Windows: C:\\Users\\<user>\\AppData\\Local\\pygame

    Returns:
        The absolute path to the projects directory.
    """
    projects_dir = appdirs.user_data_dir(ORG, appauthor=False)
    os.makedirs(projects_dir, exist_ok=True)
    return projects_dir


def get_path(name: str) -> str:
    """Return the path to the named project directory.
    Does NOT create the directory - only returns the path where it would be.

    Args:
        name: The project name.

    Returns:
        The absolute path to the project directory.

    Raises:
        ValueError: If the project name is invalid.
    """
    _validate_name(name)
    projects_path = get_projects_path()
    return os.path.join(projects_path, name)


def valid_project(name: str) -> bool:
    """Check if the named project appears to be valid.

    A valid project must have:
        - A metadata.json file
        - A requirements.txt file
        - A .env directory
        - A .git directory

    Args:
        name: The project name to check.

    Returns:
        True if all required files/directories exist, False otherwise.
    """
    path = get_path(name)

    metadata_file = os.path.join(path, "metadata.json")
    req_file = os.path.join(path, "requirements.txt")
    env_dir = os.path.join(path, ".env")
    git_dir = os.path.join(path, ".git")
    valid = (
        os.path.isfile(metadata_file)
        and os.path.isfile(req_file)
        and os.path.isdir(env_dir)
        and os.path.isdir(git_dir)
    )
    return valid


def _validate_name(name: str) -> None:
    """Validate a project name according to safety rules.

    Args:
        name: The project name to validate.

    Raises:
        ValueError: If the name violates any of these rules:
            - Must be a non-empty string
            - Must not contain path separators ('/' or '\\') or NUL
            - Must not be '.' or '..' or start with a '.'
            - Must not have leading or trailing whitespace
    """
    if not isinstance(name, str) or not name:
        raise ValueError("project name must be a non-empty string")

    if "/" in name or "\\" in name or "\0" in name:
        raise ValueError("project name must not contain path separators or NUL")

    if name in {".", ".."} or name.startswith("."):
        raise ValueError("project name must not be '.' or '..' or start with a '.'")

    if name != name.strip():
        raise ValueError("project name must not have leading or trailing whitespace")
