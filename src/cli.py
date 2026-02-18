from . import version
from .manager import *
import argparse


def cli():
    parser = argparse.ArgumentParser(prog="pygame", description="pygame CLI")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"v{version}",
        help="Show the version of pygame",
    )

    subparsers = parser.add_subparsers(
        dest="Action", required=True, help="Action to run"
    )

    # new
    parser_new = subparsers.add_parser(
        "new", aliases=["create", "setup", "init"], help="Create a new project"
    )
    parser_new.add_argument("name", help="The name of the new project")
    parser_new.add_argument(
        "--description", "-d", default="", help="An optional description of the project"
    )
    parser_new.add_argument(
        "--author",
        "-a",
        default="",
        help="The name of the project author/studio (default: current system user)",
    )

    parser_new.add_argument(
        "--tags",
        "-t",
        nargs="*",
        default=[],
        help="Space-separated list of tags (e.g., --tags 2d prototype platformer)",
    )

    parser_new.add_argument(
        "--input",
        "-i",
        action="store_true",
        help="Use terminal input to parse the project data",
    )

    parser_new.set_defaults(func=new_project)

    # run
    parser_run = subparsers.add_parser(
        "run", aliases=["start","open","play"], help="Run a project"
    )
    parser_run.add_argument("name", help="The name of the project to run")
    parser_run.add_argument(
        "--web", "-w", action="store_true", help="Use the web to run"
    )
    parser_run.add_argument("--cdn", help="CDN URL for pygbag")
    parser_run.add_argument("--template", help="Template for pygbag")
    parser_run.set_defaults(func=run_project)

    # explore
    parser_explore = subparsers.add_parser(
        "explore",
        aliases=["browse", "folder", "files"],
        help="Open the project folder in the file manager",
    )
    parser_explore.add_argument("name", help="The name of the project to explore")
    parser_explore.set_defaults(func=explore_projects)

    # rename
    parser_rename = subparsers.add_parser("rename", help="Rename a project")
    parser_rename.add_argument("old_name", help="The old name of the project")
    parser_rename.add_argument("new_name", help="The new name of the project")
    parser_rename.set_defaults(func=rename_project)

    # delete
    parser_delete = subparsers.add_parser(
        "delete", aliases=["remove", "del", "rm"], help="Delete a project"
    )
    parser_delete.add_argument("name", help="The name of the project to delete")
    parser_delete.add_argument(
        "--force",
        action="store_true",
        help="Do not ask for confirmation before deleting the project",
    )
    parser_delete.set_defaults(func=delete_project)

    # format
    parser_format = subparsers.add_parser(
        "format", aliases=["reset"], help="Delete all projects "
    )
    parser_format.add_argument(
        "--force",
        action="store_true",
        help="Do not ask for confirmation before deleting all the projects",
    )
    parser_format.set_defaults(func=format_projects)

    # build
    parser_build = subparsers.add_parser(
        "build", aliases=["make", "compile"], help="Build the project"
    )
    parser_build.add_argument("name", help="The name of the project to build")
    parser_build.add_argument(
        "--web", "-w", action="store_true", help="Use the web builder"
    )
    parser_build.add_argument("--cdn", help="CDN URL for pygbag")
    parser_build.add_argument("--template", help="Template for pygbag")
    parser_build.set_defaults(func=build_project)

    # info
    parser_info = subparsers.add_parser(
        "info", aliases=["metadata"], help="Show the project metadata"
    )
    parser_info.add_argument("name", help="The name of the project")
    parser_info.set_defaults(func=info_project)

    # list
    parser_list = subparsers.add_parser(
        "list", aliases=["ls"], help="List all projects"
    )
    parser_list.set_defaults(func=list_projects)

    # clone
    parser_clone = subparsers.add_parser(
        "clone",aliases=["git"], help="Clone a Git repository as a new project"
    )
    parser_clone.add_argument("source", help="Git repository URL (HTTPS or SSH)")
    parser_clone.add_argument("--name", "-n", help="Custom name for the cloned project")
    parser_clone.set_defaults(func=clone_project)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
