# pygame-manager
![PyPI - Version](https://img.shields.io/pypi/v/pygame-manager)
![Tests](https://img.shields.io/github/actions/workflow/status/AntonisPylos/pygame-manager/run_tests.yml)
![License](https://img.shields.io/github/license/AntonisPylos/pygame-manager)
![PyPI - Status](https://img.shields.io/pypi/status/pygame-manager)

A CLI project management tool for pygame community edition.

## Features

- Create new projects with metadata
- Manage multiple projects via the terminal
- Run projects locally or in browser (pygbag)
- Build projects for distribution (cx_Freeze)
- Clone projects directly from Git repositories 

## Getting Started

Install:
```bash
pip install pygame-manager
```

Basic Example:
```bash
# Create a new project
pygame new my_game

# Run the project
pygame run my_game

# List all projects
pygame list

# Build for distribution
pygame build my_game

```

To see all available commands:

```bash
pygame --help
```

## Command Aliases

You can use any of these aliases: `pygame` `pygame-ce` `pgce`

## License

This project is licensed under the MIT License.
See the [`LICENSE.txt`](LICENSE.txt) file for the full license text.

