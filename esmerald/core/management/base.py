"""
Base classes for writing management directives (named directives which can
be rund through `esmerald-admin`).
"""
import argparse
import os
import sys
from typing import Any, Dict

import esmerald
from esmerald.core.management.exceptions import DirectiveError, SystemCheckError
from esmerald.core.management.formatters import EsmeraldHelpFormatter, OutputWrapper
from esmerald.core.management.parsers import DirectiveParser


class BaseDirective:
    """
    The base class from which all management directives derive.
    """

    help = ""

    _called_from_command_line = False
    base_stealth_options = ("stderr", "stdout")
    stealth_options = ()
    suppressed_base_arguments = set()

    def __init__(self, stdout=None, stderr=None):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)

    def get_version(self):
        """
        Returns the current version of Esmerald.
        """
        return esmerald.__version__

    def create_parser(self, prog_name: Any, subdirective: Any, **kwargs: Dict[str, Any]):
        """
        Create and return the ``ArgumentParser`` which will be used to
        parse the arguments to this directive.
        """
        kwargs.setdefault("formatter_class", EsmeraldHelpFormatter)
        parser = DirectiveParser(
            prog="%s %s" % (os.path.basename(prog_name), subdirective),
            description=self.help or None,
            missing_args_message=getattr(self, "missing_args_message", None),
            called_from_command_line=getattr(self, "_called_from_command_line", None),
            **kwargs,
        )
        self.add_base_argument(
            parser,
            "--version",
            action="version",
            version=self.get_version(),
            help="Show program's version number and exit.",
        )
        self.add_base_argument(
            parser,
            "-v",
            "--verbosity",
            default=1,
            type=int,
            choices=[0, 1, 2, 3],
            help=(
                "Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, "
                "3=very verbose output"
            ),
        )
        self.add_base_argument(
            parser,
            "--traceback",
            action="store_true",
            help="Raise on DirectiveError exceptions.",
        )
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser: Any):
        """
        Entrypoint for directives to add custom arguments.
        """

    def add_base_argument(self, parser: Any, *args: Any, **kwargs: Dict[str, Any]):
        for arg in args:
            if arg in self.suppressed_base_arguments:
                kwargs["help"] = argparse.SUPPRESS
                break
        parser.add_argument(*args, **kwargs)

    def print_help(self, prog_name, subdirective):
        parser = self.create_parser(prog_name, subdirective)
        parser.print_help()

    def run_from_argv(self, argv: Any):
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])

        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop("args", ())
        try:
            self.run(*args, **cmd_options)
        except DirectiveError as e:
            if options.traceback:
                raise
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write("%s: %s" % (e.__class__.__name__, e))
            sys.exit(e.returncode)

    def run(self, *args: Any, **options: Dict[str, Any]):
        if options.get("stdout"):
            self.stdout = OutputWrapper(options["stdout"])
        if options.get("stderr"):
            self.stderr = OutputWrapper(options["stderr"])

        output = self.handle(*args, **options)
        if output:
            self.stdout.write(output)
        return output

    def handle(self, *args: Any, **options: Dict[str, Any]):
        """
        The logic of the directive. Subclasses must implement this method.
        """
        raise NotImplementedError("subclasses of BaseDirective must provide a handle() method")
