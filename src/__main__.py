from .cli import cli
from sys import argv

# ASCII Art font: Future
show_art = lambda: print(
    r""" ____ ___  _ _____ ____  _      _
/  __\\  \///  __//  _ \/ \__/|/  __/
|  \/| \  / | |  _| / \|| |\/|||  \ 
|  __/ / /  | |_//| |-||| |  |||  /_
\_/   /_/   \____\\_/ \|\_/  \|\____\                                                        
""",
    end="",
)

show_help = lambda: print(
    """Usage: pygame <command> [options]
Run 'pygame --help' to see all commands
""",
    end="",
)


def main():
    if len(argv) == 1:
        show_art()
        show_help()
        return
    cli()


if __name__ == "__main__":
    main()
