from inspect import getdoc
from docopt import docopt
from docopt import DocoptExit


def get_docopt_help(docstring, *args, **kwargs):
    try:
        return docopt(docstring, *args, **kwargs)
    except DocoptExit:
        raise SystemExit(docstring)


class DocoptDispatcher:
    def __init__(self, command_cls, **options):
        self.command_cls = command_cls
        self.options = options

    def parse(self, argv):
        command_help = getdoc(self.command_cls) + "\n"
        options = get_docopt_help(command_help, argv, **self.options)
        command = options["COMMAND"]

        if command is None:
            raise SystemExit(command_help)

        if not hasattr(self.command_cls, command):
            print(f'Command "{command}" not found \n')
            raise SystemExit(command_help)

        handler = getattr(self.command_cls, command)
        docstring = getdoc(handler)

        command_options = get_docopt_help(
            docstring, options["ARGS"], options_first=False
        )

        return handler, command_options
