"""The create command."""


from json import dumps
from os.path import exists, join

from docopt import docopt

from lib import path_check, query_yes_no
from models import create_album

from .base import BaseCommand


class Create(BaseCommand):
    """
    Create a image album (database) location. If <album-name> is ommited then 'default' is used.

    usage:
        iment create [-n <album-name>] [-l <location>]

    options:
        -n, --name  Name to reference the album by, defaults to 'default'
        -d, --dir   Directiory to store the database file, defaults to '~/.config/iment/'
    """

    def run(self):
        # TODO: Perhaps look into PyInquirer for a questionaire style setup (when we have more questions) perhaps DB setup?
        # if len(self.options) < 1:
        #     args = docopt(Create.__doc__, version='1.0.0')
        #     raise DocoptExit()

        dry_run = self.global_options['--dry-run']
        album_name = self.get_option_value(['-n', '--name'], 'default')
        dirname = path_check(self.get_option_value(['-d', '--dir'], '~/.config/iment/'))

        if not dirname:
            raise Exception("Directiry does not exist {}".format(db_filepath))

        db_filepath = '{}.db'.format(join(dirname, album_name))

        proceed = True
        if exists(db_filepath):
            proceed = query_yes_no("Album with that name already exisit, overwrite it?")

        print('Creating new album "{}"!'.format(album_name))

        if proceed:
            print('Creating SQLite Db file: {}'.format(db_filepath))
            if not dry_run:
                db_connection_uri = 'sqlite:///{}'.format(db_filepath)
                create_album(db_connection_uri)
                # update the config with the db connection string
                self.config.add_album(db_connection_uri, album_name)
