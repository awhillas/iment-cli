"""The base command."""


class BaseCommand(object):
    """A base command."""

    def __init__(self, config, options, global_options, *args, **kwargs):
        self.config = config
        self.options = options
        self.global_options = global_options
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')
