#! /usr/bin/env python
"""
Control center for an imaginary video game.

usage:
    iment [-hv] <command> [<args>...]

options:
    -h, --help      Show detailed help
    -v, --version   shows the version

The subcommands are:
    add     Add files to the library
    create  Create a new library
"""

from docopt import docopt
from docopt import DocoptExit
from pprint import pprint as pp

import commands

if __name__ == '__main__':
    args = docopt(__doc__, version='1.0.0', options_first=True)

    # Retrieve the command to execute.
    command_name = args.pop('<command>').capitalize()

    # Retrieve the command arguments.
    command_args = args.pop('<args>')
    if command_args is None:
        command_args = {}

    # After 'poping' '<command>' and '<args>', what is left in the args dictionary are the global arguments.

    # Retrieve the class from the 'commands' module.
    try:
        command_class = getattr(commands, command_name)
    except AttributeError:
        print('Unknown command. RTFM!.')
        raise DocoptExit()

    # Create an instance of the command.
    command = command_class(command_args, args)

    # Execute the command.
    command.run()