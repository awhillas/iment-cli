from pprint import pprint as pp

from tabulate import tabulate

from models import Image, Location

from .base import BaseCommand


class Ls(BaseCommand):
    """
    List all the images and their details

    usage:
        iment ls [-a <YYYY-MM-DD>] [-b <YYYY-MM-DD>] [-t <tag>,<tag>...] [--type <image-type>]

    options:
        -b, --before    Filter images before a date/time
        -a, --after     Filter images after a date/time
        -t, --tag       Filter by comma sperated list of tags
        --type          Filter by image type i.e. gif,jpeg,png etc
    """

    def run(self):
        album = self.config.get_album()
        query = album.query(Image, Location).all().join(Location)
        rows = [[img.id, img.name] for img in query]
        print(tabulate(rows, headers=['id', 'name']))
