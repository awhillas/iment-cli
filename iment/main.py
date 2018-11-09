#! /usr/bin/env python
"""
Control center for an imaginary video game.

usage:
    iment [-hvd] [-a <album>] [-c <config>] <command> [<args>...]

options:
    -h, --help      Show detailed help.
    -v, --version   Shows the version.
    -d, --dry-run   Dry run of command, just lists changes,
    -a <album>      Album reference, "default" is assumed if not given.
    -c <config>     Alternative config file, defaults to "~/.config/iment/config.yml"

The subcommands are:
    add     Add files to the album
    create  Create a new album
    ls      List images in album
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
    # print(args)

    # Retrieve the class from the 'commands' module.
    try:
        command_class = getattr(commands, command_name)
    except AttributeError:
        print('Unknown command?')
        print(Figlet(font='big').renderText('RTFM!'))
        raise DocoptExit()

    # Open config file
    config_file = args['-c'] if args['-c'] else '~/.config/iment/config.yml'
    config = Config(config_file)

    # Create an instance of the command.
    command = command_class(config, command_args, args)

    print(Figlet(font='isometric3').renderText('iMENT'))

    # Execute the command.
    command.run()
