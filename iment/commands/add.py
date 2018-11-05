"""The hello command."""


from json import dumps
from pprint import pprint as pp

from .base import Base


class Add(Base):
    """
    Add all the images at the <location> into the library database (not move them!)

    usage:
        add <location> (-r | --recurse) (--move) (--tag=<tag1,tag2,tag3,etc>)

    options:
        <location>  Where to look for images
        -r, --recurse   Look recursivly into sub directories.
        --tag           Tag all the images with the given tag names as they are imported.
        --move          Move the images to the default location.
    """

    def run(self):
        print('Add, world!')
        pp(self.options)
        print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))
