"""The create command."""


from json import dumps
from docopt import docopt

from .base import Base


class Create(Base):
    """
    Create a image library database.

    usage:
        iment create [<library>]

    options:
    """

    def run(self):
        if len(self.options) < 1:
            args = docopt(Create.__doc__, version='1.0.0')
            raise DocoptExit()

        print('Create, world!')
        print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))
