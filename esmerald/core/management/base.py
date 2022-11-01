"""
Base classes for writing management directives (named directives which can
be executed through `esmerald-admin`).
"""
import argparse
import os
import sys
from argparse import ArgumentParser, HelpFormatter
from io import TextIOBase
from typing import Any, Dict, Optional

import esmerald
from esmerald.core.management.color import color_style, no_style


class DirectiveError(Exception):
    """
    Exception class indicating a problem while executing a directive.
    """

    def __init__(self, *args: Any, returncode: int = 1, **kwargs: Dict[str, Any]):
        self.returncode = returncode
        super().__init__(*args, **kwargs)


class SystemCheckError(DirectiveError):
    """
    The system check framework detected unrecoverable errors.
    """

    ...


class DirectiveParser(ArgumentParser):
    """
    Customized ArgumentParser class to improve some error messages and prevent SystemExit.
    """

    def __init__(
        self,
        *,
        missing_args_message: Optional[str] = None,
        called_from_command_line: Optional[Any] = None,
        **kwargs: Dict[str, Any]
    ):
        self.missing_args_message = missing_args_message
        self.called_from_command_line = called_from_command_line
        super().__init__(**kwargs)

    def parse_args(self, args: Any = None, namespace: str = None):
        if self.missing_args_message and not (
            args or any(not arg.startswith("-") for arg in args)
        ):
            self.error(self.missing_args_message)
        return super().parse_args(args, namespace)

    def error(self, message):
        if self.called_from_command_line:
            super().error(message)
        else:
            raise DirectiveError("Error: %s" % message)


def handle_default_options(options: Any):
    """
    Include any default options that all directives should accept here
    so that ManagementUtility can handle them before searching for
    user directives.
    """
    if options.pythonpath:
        sys.path.insert(0, options.pythonpath)


class EsmeraldHelpFormatter(HelpFormatter):
    """
    Customized formatter so that command-specific arguments appear in the
    --help output before arguments common to all directives.
    """

    show_last = {
        "--version",
        "--verbosity",
        "--traceback",
        "--settings",
        "--pythonpath",
        "--no-color",
        "--force-color",
    }

    def _reordered_actions(self, actions: Any):
        return sorted(actions, key=lambda a: set(a.option_strings) & self.show_last != set())

    def add_usage(self, usage: str, actions: Any, *args: Any, **kwargs: Dict[str, Any]):
        super().add_usage(usage, self._reordered_actions(actions), *args, **kwargs)

    def add_arguments(self, actions: Any):
        super().add_arguments(self._reordered_actions(actions))


class OutputWrapper(TextIOBase):
    @property
    def style_func(self):
        return self._style_func

    @style_func.setter
    def style_func(self, style_func: Any):
        if style_func and self.isatty():
            self._style_func = style_func
        else:
            self._style_func = lambda x: x

    def __init__(self, out: Any, ending="\n"):
        self._out = out
        self.style_func = None
        self.ending = ending

    def __getattr__(self, name: str):
        return getattr(self._out, name)

    def flush(self):
        if hasattr(self._out, "flush"):
            self._out.flush()

    def isatty(self):
        return hasattr(self._out, "isatty") and self._out.isatty()

    def write(
        self,
        msg: str = "",
        style_func: Optional[Any] = None,
        ending: Optional[Any] = None,
    ):
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = style_func or self.style_func
        self._out.write(style_func(msg))


class BaseDirective:
    """
    The base class from which all management directives ultimately
    derive.

    Use this class if you want access to all of the mechanisms which
    parse the command-line arguments and work out what code to call in
    response; if you don't need to change any of that behavior,
    consider using one of the subclasses defined in this file.

    If you are interested in overriding/customizing various aspects of
    the command-parsing and -execution behavior, the normal flow works
    as follows:

    1. ``esmerald-admin`` loads the command class and calls its ``run_from_argv()`` method.

    2. The ``run_from_argv()`` method calls ``create_parser()`` to get
       an ``ArgumentParser`` for the arguments, parses them, performs
       any environment changes requested by options like
       ``pythonpath``, and then calls the ``execute()`` method,
       passing the parsed arguments.

    3. The ``execute()`` method attempts to carry out the command by
       calling the ``handle()`` method with the parsed arguments; any
       output produced by ``handle()`` will be printed to standard
       output and, if the command is intended to produce a block of
       SQL statements, will be wrapped in ``BEGIN`` and ``COMMIT``.

    4. If ``handle()`` or ``execute()`` raised any exception (e.g.
       ``DirectiveError``), ``run_from_argv()`` will  instead print an error
       message to ``stderr``.

    Thus, the ``handle()`` method is typically the starting point for
    subclasses; many built-in directives and command types either place
    all of their logic in ``handle()``, or perform some additional
    parsing work in ``handle()`` and then delegate from it to more
    specialized methods as needed.

    Several attributes affect behavior at various steps along the way:

    ``help``
        A short description of the command, which will be printed in
        help messages.

    ``output_transaction``
        A boolean indicating whether the command outputs SQL
        statements; if ``True``, the output will automatically be
        wrapped with ``BEGIN;`` and ``COMMIT;``. Default value is
        ``False``.

    ``requires_migrations_checks``
        A boolean; if ``True``, the command prints a warning if the set of
        migrations on disk don't match the migrations in the database.

    ``requires_system_checks``
        A list or tuple of tags, e.g. [Tags.staticfiles, Tags.models]. System
        checks registered in the chosen tags will be checked for errors prior
        to executing the command. The value '__all__' can be used to specify
        that all system checks should be performed. Default value is '__all__'.

        To validate an individual application's models
        rather than all applications' models, call
        ``self.check(app_configs)`` from ``handle()``, where ``app_configs``
        is the list of application's configuration provided by the
        app registry.

    ``stealth_options``
        A tuple of any options the command uses which aren't defined by the
        argument parser.
    """

    # Metadata about this command.
    help = ""

    _called_from_command_line = False
    output_transaction = False  # Whether to wrap the output in a "BEGIN; COMMIT;"
    base_stealth_options = ("stderr", "stdout")
    stealth_options = ()
    suppressed_base_arguments = set()

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)
        if no_color and force_color:
            raise DirectiveError("'no_color' and 'force_color' can't be used together.")
        if no_color:
            self.style = no_style()
        else:
            self.style = color_style(force_color)
            self.stderr.style_func = self.style.ERROR

    def get_version(self):
        """
        Return the Esmerald version, which should be correct for all built-in
        Esmerald directives. User-supplied directives can override this method to
        return their own version.
        """
        return esmerald.__version__

    def create_parser(self, prog_name: Any, subdirective: Any, **kwargs: Dict[str, Any]):
        """
        Create and return the ``ArgumentParser`` which will be used to
        parse the arguments to this command.
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
            "--settings",
            help=(
                "The Python path to a settings module, e.g. "
                '"myproject.settings.main". If this isn\'t provided, the '
                "ESMERALD_SETTINGS_MODULE environment variable will be used."
            ),
        )
        self.add_base_argument(
            parser,
            "--pythonpath",
            help=(
                "A directory to add to the Python path, e.g. "
                '"/home/esmeraldprojects/myproject".'
            ),
        )
        self.add_base_argument(
            parser,
            "--traceback",
            action="store_true",
            help="Raise on DirectiveError exceptions.",
        )
        self.add_base_argument(
            parser,
            "--no-color",
            action="store_true",
            help="Don't colorize the command output.",
        )
        self.add_base_argument(
            parser,
            "--force-color",
            action="store_true",
            help="Force colorization of the command output.",
        )
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser: Any):
        """
        Entry point for subclassed directives to add custom arguments.
        """

    def add_base_argument(self, parser: Any, *args: Any, **kwargs: Dict[str, Any]):
        """
        Call the parser's add_argument() method, suppressing the help text
        according to BaseDirective.suppressed_base_arguments.
        """
        for arg in args:
            if arg in self.suppressed_base_arguments:
                kwargs["help"] = argparse.SUPPRESS
                break
        parser.add_argument(*args, **kwargs)

    def print_help(self, prog_name, subdirective):
        """
        Print the help message for this command, derived from
        ``self.usage()``.
        """
        parser = self.create_parser(prog_name, subdirective)
        parser.print_help()

    def run_from_argv(self, argv: Any):
        """
        Set up any environment changes requested (e.g., Python path
        and Esmerald settings), then run this command. If the
        command raises a ``DirectiveError``, intercept it and print it sensibly
        to stderr. If the ``--traceback`` option is present or the raised
        ``Exception`` is not ``DirectiveError``, raise it.
        """
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])

        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop("args", ())
        handle_default_options(options)
        try:
            self.execute(*args, **cmd_options)
        except DirectiveError as e:
            if options.traceback:
                raise

            # SystemCheckError takes care of its own formatting.
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write("%s: %s" % (e.__class__.__name__, e))
            sys.exit(e.returncode)

    def execute(self, *args: Any, **options: Dict[str, Any]):
        """
        Try to execute this command, performing system checks if needed (as
        controlled by the ``requires_system_checks`` attribute, except if
        force-skipped).
        """
        if options["force_color"] and options["no_color"]:
            raise DirectiveError(
                "The --no-color and --force-color options can't be used together."
            )
        if options["force_color"]:
            self.style = color_style(force_color=True)
        elif options["no_color"]:
            self.style = no_style()
            self.stderr.style_func = None
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
        The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError("subclasses of BaseDirective must provide a handle() method")
