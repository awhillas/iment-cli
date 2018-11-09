from os.path import join, dirname, basename
from pprint import pprint as pp

from yaml import dump, load

from lib import path_check
from models import open_album

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


DEFAULT_CONFIG = { 'albums': {} }

class Config(object):
    """ Manage the YML config file """
    def __init__(self, filepath=None):
        self.path = path_check(filepath)
        if self.path:
            print("Using config file: {}".format(self.path))
            with open(self.path) as f:
                self.data = load(f.read(), Loader=Loader)
        else:
            self.data = DEFAULT_CONFIG
            self.path = join(path_check(dirname(filepath), True), basename(filepath))
            self.save()

    def get(self):
        return self.data

    def save(self):
        """ Write changes to disk """
        output = dump(self.data, Dumper=Dumper, default_flow_style=False)
        with open(self.path, 'w') as f:
            f.write(output)

    def update(self, obj:dict):
        """ Merge the given object with the current dict """
        self.data.update(obj)
        self.save()  # Should we do this every time...?

    def add_album(self, connection_uri:str, name:str='default'):
        """ Add a new album (database) """
        self.data['albums'][name] = connection_uri
        self.save()

    def get_album(self, name:str=None):
        """ Check that the given album exists (try 'default' if not given) """
        album = name if name else 'default'
        if album in self.data['albums']:
            return open_album(self.data['albums'][album])
        else:
            pp(self.data)
            raise Exception("Album '{}', is like, unknown to us at this time, man...".format(album))
