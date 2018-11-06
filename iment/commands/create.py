"""The create command."""


from json import dumps
from os.path import join, expanduser, exists

from docopt import docopt

from .base import BaseCommand
from lib import query_yes_no
from models import create_album


class Create(BaseCommand):
    """
    Create a image library database.

    usage:
        iment create [ <album-name> ]
    """

    def run(self):
        # TODO: Perhaps look into PyInquirer for a questionaire style setup (when we have more questions)
        # if len(self.options) < 1:
        #     args = docopt(Create.__doc__, version='1.0.0')
        #     raise DocoptExit()

        dry_run = self.global_options['--dry-run']
        album_name = self.options[0] if len(self.options) else 'default'

        print('Creating new album "{}"!'.format(album_name))

        db_filepath = '{}.db'.format(join(expanduser('~/.config/iment/'), album_name))

        proceed = True
        if exists(db_filepath):
            proceed = query_yes_no("Album with that name already exisit, overwrite it?")

        if proceed:
            print('Creating SQLite Db file: {}'.format(db_filepath))
            if not dry_run:
                db_connection_uri = 'sqlite:///{}'.format(db_filepath)

                create_album(db_connection_uri)

                # update the config with the db connection string
                self.config.add_album(db_connection_uri, album_name)
