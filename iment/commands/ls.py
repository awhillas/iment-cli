from pprint import pprint as pp

from tabulate import tabulate

from models import Image, Location

from .base import BaseCommand


class Ls(BaseCommand):
    """
    List all the images and their details

    usage:
        ls

    options:
    """

    def run(self):
        album = self.config.get_album()
        rows = [[img.id, img.name] for img in album.query(Image).all()]
        print(tabulate(rows, headers=['id', 'name']))
