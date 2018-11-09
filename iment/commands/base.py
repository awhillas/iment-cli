from os.path import expanduser, abspath, exists


class BaseCommand(object):
    """A base command."""

    def __init__(self, config, options, global_options, *args, **kwargs):
        self.config = config
        self.options = options
        self.global_options = global_options
        self.args = args
        self.album = global_options['-a'] if global_options['-a'] else 'default'
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')

    def option_is_set(self, needles:list):
        # TODO: find a better arg parser which can handle subcommands
        return any(n in self.options for n in needles)

    def get_flag_value(self, flags:list):
        """ Return the value for the given option.
            :param option: A list of flags for the same option i.e. ['-h', '--help'] """
        for f in flags:
            if f in self.options:
                return self.options[self.options.index(f) + 1]

    def get_option_value(self, flags, default):
        """ For the given option flags return the value """
        return self.get_flag_value(flags) if self.option_is_set(flags) else default