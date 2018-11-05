"""
Control center for an imaginary video game.
usage:
    control [-hv] [-n NAME] <command> [<args>...]

options:
    -h, --help                  shows the help
    -n NAME --name=NAME         sets player name [default: player]
    -v, --version               shows the version

The subcommands are:
    create  Create a new library database
    import  Import images into a library
    gather  Move all the images into a single location
"""


from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main CLI entrypoint."""
    import iment.commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items():
        if hasattr(iment.commands, k) and v:
            module = getattr(iment.commands, k)
            iment.commands = getmembers(module, isclass)
            command = [command[1] for command in iment.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
