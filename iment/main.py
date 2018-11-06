#! /usr/bin/env python
"""
Control center for an imaginary video game.

usage:
    iment [-hvd] <command> [<args>...]

options:
    -h, --help      Show detailed help
    -v, --version   Shows the version
    -d, --dry-run   Dry run of command, just lists changes

The subcommands are:
    add     Add files to the library
    create  Create a new library
"""

import commands
from pprint import pprint as pp

from docopt import DocoptExit, docopt
from pyfiglet import Figlet

from configment import Config

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
        print('Unknown command?')
        print(Figlet(font='big').renderText('RTFM!'))
        raise DocoptExit()

    # Open config file
    print(args)
    config = Config()  # TODO: Pass in optional config name if given

    # Create an instance of the command.
    command = command_class(config, command_args, args)

    print(Figlet(font='isometric3').renderText('iMENT'))

    # Execute the command.
    command.run()
