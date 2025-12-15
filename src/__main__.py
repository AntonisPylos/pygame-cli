import argparse
from sys import argv


# ASCII Art font: Future
show_art = lambda: print(
r"""
 ____ ___  _ _____ ____  _      _____      ____ _     _ 
/  __\\  \///  __//  _ \/ \__/|/  __/     /   _Y \   / \
|  \/| \  / | |  _| / \|| |\/|||  \ _____ |  / | |   | |
|  __/ / /  | |_//| |-||| |  |||  /_\____\|  \_| |_/\| |
\_/   /_/   \____\\_/ \|\_/  \|\____\     \____|____/\_/                                                       
""", end="")

def main():
    len(argv) == 1 and show_art()



if __name__ == "__main__":
    main()