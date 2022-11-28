import os
import sys
from collections import defaultdict
from difflib import get_close_matches

import esmerald
from esmerald.core.management.base import BaseDirective, DirectiveError, DirectiveParser
from esmerald.core.management.utils import get_directives, load_directive_class


class ManagementUtility:
    location = __path__[0]

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])

    def main_help_text(self, directives_only=False):
        if directives_only:
            usage = sorted(get_directives(self.location))
        else:
            usage = [
                "",
                "Type '%s help <subdirective>' for help on a specific subdirective."
                % self.prog_name,
                "",
                "Available subdirectives:",
            ]
            directives_dict = defaultdict(lambda: [])
            for name, app in get_directives().items():
                if app == "esmerald.core":
                    app = "esmerald"
                else:
                    app = app.rpartition(".")[-1]
                directives_dict[app].append(name)

        return "\n".join(usage)

    def fetch_directive(self, subdirective):
        directives = get_directives(self.location)
        try:
            app_name = directives[subdirective]
        except KeyError:
            possible_matches = get_close_matches(subdirective, directives)
            sys.stderr.write("Unknown command: %r" % subdirective)
            if possible_matches:
                sys.stderr.write(". Did you mean %s?" % possible_matches[0])
            sys.stderr.write("\nType '%s help' for usage.\n" % self.prog_name)
            sys.exit(1)
        if isinstance(app_name, BaseDirective):
            # If the command is already loaded, use it directly.
            klass = app_name
        else:
            klass = load_directive_class(app_name, subdirective)
        return klass

    def run(self):
        try:
            subdirective = self.argv[1]
        except IndexError:
            subdirective = "help"

        parser = DirectiveParser(
            prog=self.prog_name,
            usage="%(prog)s subdirective [options] [args]",
            add_help=False,
            allow_abbrev=False,
        )
        parser.add_argument("args", nargs="*")
        try:
            options, args = parser.parse_known_args(self.argv[2:])
        except DirectiveError:
            pass

        if subdirective == "help":
            if "--directives" in args:
                sys.stdout.write(self.main_help_text(directives_only=True) + "\n")
            elif not options.args:
                sys.stdout.write(self.main_help_text() + "\n")
            else:
                self.fetch_directive(options.args[0]).print_help(self.prog_name, options.args[0])
        elif subdirective == "version" or self.argv[1:] == ["--version"]:
            sys.stdout.write(esmerald.__version__ + "\n")
        elif self.argv[1:] in (["--help"], ["-h"]):
            sys.stdout.write(self.main_help_text() + "\n")
        else:
            self.fetch_directive(subdirective).run_from_argv(self.argv)


def run_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.run()
