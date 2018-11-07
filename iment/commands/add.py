"""The hello command."""

from json import dumps
from os import walk
from os.path import basename, exists, isdir, join
from pprint import pprint as pp

import dhash
from PIL import Image

from lib import is_image
from models import Image, Location

from .base import BaseCommand


class Add(BaseCommand):
    """
    Add all the images at the <location> into the library database (not move them!)

    usage:
        add [-rm] [-t <tag> <tag>...] <location>

    options:
        <location>  Where to look for images
        -r, --recurse   Look recursivly into sub directories.
        -t, --tag       Tag all the images with the given tag names as they are imported.
        -m, --move      Move the images to the default location.
        -u, --update    Update metadata if duplicate paths exist.
    """

    def run(self):
        print('Adding files...')
        if len(self.options) < 1:
            args = docopt(Create.__doc__, version='1.0.0')
            raise DocoptExit()

        # options processing

        dry_run = self.global_options['--dry-run']
        where = self.options[-1]
        can_update = self.option_is_set(['-u', '--update'])
        can_move = self.option_is_set(['-m', '--move'])
        can_recurse = self.option_is_set(['-r', '--recurse'])
        pp(self.options)

        # Find the file(s)

        if exists(where):
            filepaths = []
            if isdir(where):
                for (root, dirs, files) in walk(where):
                    for f in files:
                        path = join(root, f)
                        image_type = is_image(path)
                        if image_type:
                            image = Image.open(path)
                            row, col = dhash.dhash_row_col(image)
                            print(dhash.format_hex(row, col))
                            print("Found: {}".format(path))
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
        album = self.config.get_album()
        if len(filepaths) and not dry_run:
            album = self.config.get_album()
            existing = album.query(Location).filter(Location.filepath.in_([f['path'] for f in filepaths])).all()
            # pp(existing)
            for i in filepaths:
                if not any(l.filepath == i['path'] for l in existing):
                    print("Adding: {}".format(i))
                    # TODO: Allow album name to be specified
                    # TODO: Extract the image metadata
                    img = Image(name=basename(i['path']))
                    album.add(img)
                    album.commit()

                    # TODO: More location types i.e. S3, FTP etc
                    loc = Location(filepath=i['path'], location_type='local', image_type=i['image_type'], image=img)
                    album.add(loc)
                    album.commit()
                else:
                    print("Already in album, skipping: {}".format(i['path']))
