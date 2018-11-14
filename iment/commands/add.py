import imghdr
from datetime import datetime
from functools import reduce
from json import dumps
from os import remove, walk
from os.path import basename, exists, getmtime, isdir, join
from pprint import pprint as pp

import dhash
import pybktree
from docopt import DocoptExit, docopt
from PIL import Image as PilImage
from tabulate import tabulate

from lib import get_exif, path_check, print_table, query_options, print_vertical_table
from models import Image, Location

from .base import BaseCommand

# Rough list of supported image extensions that Pillow supports
PIL_SUPPORTED_IMAGES = ['.bmp',
'.eps', '.gif', '.icns', '.ico', '.im', '.jpg', '.jpeg', '.j2k', '.j2p', '.jpx', '.jfif', '.msp', '.pcx',
'.png', '.ppm', '.sgi','.spi', '.tga', '.tif', '.tiff', '.webp', '.xbm'
]

# Hamming distance between two image fingerprints that considers them the same
SIMILAR_BIT_DIFF = 1

def get_creation_time(image, path):
    meta = get_exif(image)
    if 'DateTimeOriginal' in meta:
        print('Using DateTimeOriginal', meta['DateTimeOriginal'])
        return datetime.strptime(meta['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
    elif 'DateTimeDigitized' in meta:
        print('Using DateTimeDigitized', meta['DateTimeDigitized'])
        return datetime.strptime(meta['DateTimeDigitized'], '%Y:%m:%d %H:%M:%S')
    elif 'DateTime' in meta:
        print('Using DateTime', meta['DateTime'])
        return datetime.strptime(meta['DateTime'], '%Y:%m:%d %H:%M:%S')
    else:
        print('Using file timestamp', datetime.fromtimestamp(getmtime(path)).strftime('%Y-%m-%d %H:%M:%S'))
        return datetime.fromtimestamp(getmtime(path))


class Add(BaseCommand):
    """
    Add all the images at the <location> into the library database (not move them!)

    usage:
        iment add [-rm] [-t <tag1>,<tag2>...] <location>

    options:
        <location>  Where to look for images
        -r, --recurse   Look recursivly into sub directories.
        -t, --tag       Tag all the images with the given tag names as they are imported.
        -m, --move      Move the images to the default location.
        -u, --update    Update metadata if duplicate paths exist.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fingerprints = self.config.get_fingerprints(self.album)
        self.db = self.config.get_album()

    def run(self):
        if len(self.options) < 1:
            args = docopt(Add.__doc__, version='1.0.0')
            raise DocoptExit()

        print('Adding files...')

        # options processing

        dry_run = self.global_options['--dry-run']
        where = self.options[-1]
        can_update = self.option_is_set(['-u', '--update'])
        can_move = self.option_is_set(['-m', '--move'])
        can_recurse = self.option_is_set(['-r', '--recurse'])
        tags = self.get_option_value(['-t', '--tag'], '').split(',')
        # pp(self.options)

        # Find the file(s)

        if exists(where):
            new_image_files = []
            if isdir(where):
                for (root, dirs, files) in walk(where):
                    for f in files:
                        path = join(root, f)
                        # Only "fully supported" PIL images accepted
                        if any(f.lower().endswith(ext) for ext in PIL_SUPPORTED_IMAGES):
                            new_image_files.append(path)
                        # else:
                        #     print("Skipping: {}".format(f))
                    if not can_recurse:
                        break
            else:
                # Must be a single file
                new_image_files.append(path_check(where))
        else:
            print("HEY! that don't exsist :-?")
            return

        # Read each image

        new_images = []
        for path in new_image_files:
            image = PilImage.open(path)
            if image:
                # print(path)
                fingerprint = dhash.dhash_int(image)
                width, height = image.size
                created_on = get_creation_time(image, path)
                new_images.append({
                    'filepath': path,
                    'fingerprint': str(fingerprint),
                    'dhash': fingerprint,
                    'file_format': image.format,
                    'location_type': 'local',
                    'pil_image': image,
                    'width': width,
                    'height': height,
                    'created_on': created_on
                })
            else:
                new_image_files.remove(path)
                print("Could not read {}".format(path))

        # Catalog the files

        if len(new_images):
            existing = self.db.query(Location).filter(Location.filepath.in_(new_image_files)).all()
            for img_details in new_images:
                # Do we alreay have this file/path?
                path_match = [e for e in existing if e.filepath in img_details['filepath']]
                same_loc = path_match[0] if len(path_match) else None
                # Check if we have a similar image with BK-trees, O(N log N), hA!
                # http://tech.jetsetter.com/2017/03/21/duplicate-image-detection/
                similar_hash = self.fingerprints.find(img_details['dhash'], SIMILAR_BIT_DIFF)
                # Must handle all cases:
                # +-------+-------+
                # | Path  | Hash  |
                # +-------+-------+
                # | Same  | Same  |
                # | Same  | Diff. |
                # | Diff. | Same  |
                # | Diff. | Diff  |
                # +-------+-------+
                if same_loc:
                    if similar_hash:
                        self.same_same(same_loc, img_details)
                    else:
                        self.same_paths_diff_hash(same_loc, img_details)
                else:
                    if similar_hash:
                        existing_loc = album.query(Location).filter(Location.fingerprint.is_(img_details['fingerprint']))[0]
                        self.diff_paths_same_hash(existing_loc, img_details)
                    else:
                        self.diff_diff(img_details)

        self.config.save_fingerprints(self.fingerprints, self.album)

    def same_same(self, existing_location, new_image_details):
        """ Both path and fingerprint are the same as an image in the cataloge,
            so looks like we already know about it so skip it.
            TODO: Show details side by side and ask: add location, replace, delete, skip
        """
        # print_table([vars(existing_location), new_image_details], [c.name for c in Location.__table__.columns])
        # tabulate([vars(existing_location), new_image_details], [c.name for c in Location.__table__.columns])
        print_vertical_table([vars(existing_location), new_image_details], [c.name for c in Location.__table__.columns])
        options = {
            's' : 'Skip',
            'u' : 'Update',
            'w' : 'Show',
            'd' : 'Delete',
        }
        shown = True
        while shown:
            shown = False
            answer = query_options("Already know about this image", options)
            if answer == 'r':
                self.replace_location(existing_location, new_image_details)
            elif answer == 'd':
                self.delete_location(existing_location, new_image_details)
            elif answer == 'w':
                new_image_details['pil_image'].show()
                shown = True
            else:
                print("Skipping...")

    def same_paths_diff_hash(self, existing_location, new_image_details):
        """ Same paths different hashes """
        print('same_paths_diff_hash')
        options = {
            's' : 'Skip',
            'u' : 'Update',
            'w' : 'Show',
            'd' : 'Delete',
        }
        shown = True
        while shown:
            shown = False
            answer = query_options("Already have an image at that location", options)
            if answer == 'r':
                self.replace_location(existing_location, new_image_details)
            elif answer == 'd':
                self.delete_location(existing_location, new_image_details)
            elif answer == 'w':
                new_image_details['pil_image'].show()
                shown = True
            else:
                print("Skipping...")

    def diff_paths_same_hash(self, existing_location, new_image_details):
        """ Different paths, same hashes
            TODO: confirm known similar hash exists
        """
        print("diff_paths_same_hash")
        options = {
            's' : 'Skip',
            'u' : 'Update',
            'w' : 'Show',
            'd' : 'Delete',
        }
        shown = True
        while shown:
            shown = False
            answer = query_options("Similar/Same image already in cataloge", options)
            if answer == 'a':
                self.new_location(existing_location.image, new_image_details)
            elif answer == 'r':
                self.replace_location(existing_location, new_image_details)
            elif answer == 'd':
                self.delete_location(existing_location, new_image_details)
            elif answer == 'w':
                existing = PilImage.open(existing_location.filepath)
                existing.show()
                new_image_details['pil_image'].show()
                shown = True
            else:
                print("Skipping...")

    def diff_diff(self, new_location_details:dict):
        """ Both paths and hashes are different or its completely new
            so its basically create a new image
        """
        self.new_image(new_location_details)

    def replace_location(self, old, new_details):
        print("Replacing {}...".format(old.filepath))
        image = old.image
        self.db.delete(old)
        self.new_location(image, new_details)

    def new_image(self, details:dict):
        print("Adding: {}".format(details['filepath']))
        new_image = Image(name=basename(details['filepath']))
        self.db.add(new_image)
        self.db.commit()
        self.new_location(new_image, details)

    def new_location(self, existing_image:Image, new_location_details:dict):
        """ Add a new location to an existing image """
        def sanitise(Model, data):
            return { k: data[k] for k in data if k in Model.__table__.columns }

        # print("Adding location to Image '{}'".format(existing_image.name))
        # Update the DB
        clean = sanitise(Location, new_location_details)
        loc = Location(image=existing_image, **clean)
        self.db.add(loc)
        self.db.commit()
        # Add fingerprint to BK Tree
        self.fingerprints.add(new_location_details['dhash'])

    def delete_location(self, loc, details):
        print('Deleteing file {}'.format(details['filepath']))
        remove(details['filepath'])

