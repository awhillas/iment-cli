"""The hello command."""

from os import walk
from os.path import exists, isdir, basename, join
from json import dumps
from pprint import pprint as pp

from .base import BaseCommand
from lib import is_image
from models import Location, Image


class Add(BaseCommand):
    """
    Add all the images at the <location> into the library database (not move them!)

    usage:
        add <location> [-rm] [-t <tag> <tag>...]

    options:
        <location>  Where to look for images
        -r, --recurse   Look recursivly into sub directories.
        -t, --tag       Tag all the images with the given tag names as they are imported.
        -m, --move      Move the images to the default location.
    """

    def run(self):
        print('Adding files...')
        if len(self.options) < 1:
            args = docopt(Create.__doc__, version='1.0.0')
            raise DocoptExit()

        dry_run = self.global_options['--dry-run']
        where = self.options[0]

        # Find the file(s)

        if exists(where):
            filepaths = []
            if isdir(where):
                for (root, dirs, files) in walk(where):
                    for f in files:
                        path = join(root, f)
                        image_type = is_image(path)
                        if image_type:
                            print("Adding: {}".format(path))
                            filepaths.append({ 'path': path, 'image_type': image_type })
            else:
                # Must be a single file
                image_type = is_image(path)
                if image_type:
                    filepaths.append({ 'path': path, 'image_type': image_type })
                else:
                    print('{} is not an image?'.format(path))
        else:
            print("HEY! that don't exsist :-?")
            return

        # Catalog the files

        if len(filepaths) and not dry_run:
            for i in filepaths:
                # TODO: Allow album name to be specified
                # TODO: Extract the image metadata
                album = self.config.get_album()
                img = Image(name=basename(i['path']))
                album.add(img)
                album.commit()

                # TODO: More location types i.e. S3, FTP etc
                loc = Location(filepath=i['path'], location_type='local', image_type=i['image_type'], image=img)
                album.add(loc)
                album.commit()


