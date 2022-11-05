import functools
import os
import pkgutil
import sys
from argparse import (
    _AppendConstAction,
    _CountAction,
    _StoreConstAction,
    _SubParsersAction,
)
from collections import defaultdict
from difflib import get_close_matches
from importlib import import_module

import esmerald
from esmerald.core.management.base import (
    BaseDirective,
    DirectiveError,
    DirectiveParser,
    handle_default_options,
)
from esmerald.core.management.color import color_style


def find_directives(management_dir):
    """
    Fiven a path to a management directory, retuens a list of all available directives
    """
    command_dir = os.path.join(management_dir, "directives")
    command_list = [
        name
        for _, name, is_package in pkgutil.iter_modules([command_dir])
        if not is_package and not name.startswith("_")
    ]
    return command_list


def load_directive_class(app_name, name):
    """
    Given a command name and an application name, return the Directive
    class instance. Allow all errors raised by the import process
    (ImportError, AttributeError) to propagate.
    """

    module = import_module("%s.management.directives.%s" % (app_name, name))
    return module.Directive()


@functools.lru_cache(maxsize=None)
def get_directives():
    """
    Return a dictionary mapping command names to their callback applications.

    Look for a management.directives package in esmerald.core. If a directives package exists, register all directives in that package.

    Core directives are always included. If a settings module has been
    specified, also include user-defined directives.

    The dictionary is in the format {command_name: app_name}. Key-value
    pairs from this dictionary can then be used in calls to
    load_directive_class(app_name, command_name)

    If a specific version of a command must be loaded (e.g., with the
    startapp command), the instantiated module can be placed in the
    dictionary in place of the application name.

    The dictionary is cached on the first call and reused on subsequent
    calls.
    """
    command_list = find_directives(__path__[0])
    directives = {name: "esmerald.core" for name in command_list}

    return directives


def call_command(command_name, *args, **options):
    """
    Call the given command, with the given options and args/kwargs.

    This is the primary API you should use for calling specific directives.

    `command_name` may be a string or a command object. Using a string is
    preferred unless the command object is required for further processing or
    testing.

    Some examples:
        call_command('createproject')

        from esmerald.core.management.directives import flush
        cmd = flush.Directive()
        call_command(cmd, verbosity=0, interactive=False)
        # Do something with cmd ...
    """
    if isinstance(command_name, BaseDirective):
        # Directive object passed in.
        command = command_name
        command_name = command.__class__.__module__.split(".")[-1]
    else:
        # Load the command object by name.
        try:
            app_name = get_directives()[command_name]
        except KeyError:
            raise DirectiveError("Unknown command: %r" % command_name)

        if isinstance(app_name, BaseDirective):
            # If the command is already loaded, use it directly.
            command = app_name
        else:
            command = load_directive_class(app_name, command_name)

    # Simulate argument parsing to get the option defaults (see #10080 for details).
    parser = command.create_parser("", command_name)
    # Use the `dest` option name from the parser option
    opt_mapping = {
        min(s_opt.option_strings).lstrip("-").replace("-", "_"): s_opt.dest
        for s_opt in parser._actions
        if s_opt.option_strings
    }
    arg_options = {opt_mapping.get(key, key): value for key, value in options.items()}
    parse_args = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            parse_args += map(str, arg)
        else:
            parse_args.append(str(arg))

    def get_actions(parser):
        # Parser actions and actions from sub-parser choices.
        for opt in parser._actions:
            if isinstance(opt, _SubParsersAction):
                for sub_opt in opt.choices.values():
                    yield from get_actions(sub_opt)
            else:
                yield opt

    parser_actions = list(get_actions(parser))
    mutually_exclusive_required_options = {
        opt
        for group in parser._mutually_exclusive_groups
        for opt in group._group_actions
        if group.required
    }
    # Any required arguments which are passed in via **options must be passed
    # to parse_args().
    for opt in parser_actions:
        if opt.dest in options and (opt.required or opt in mutually_exclusive_required_options):
            parse_args.append(min(opt.option_strings))
            if isinstance(opt, (_AppendConstAction, _CountAction, _StoreConstAction)):
                continue
            value = arg_options[opt.dest]
            if isinstance(value, (list, tuple)):
                parse_args += map(str, value)
            else:
                parse_args.append(str(value))
    defaults = parser.parse_args(args=parse_args)
    defaults = dict(defaults._get_kwargs(), **arg_options)
    # Raise an error if any unknown options were passed.
    stealth_options = set(command.base_stealth_options + command.stealth_options)
    dest_parameters = {action.dest for action in parser_actions}
    valid_options = (dest_parameters | stealth_options).union(opt_mapping)
    unknown_options = set(options) - valid_options
    if unknown_options:
        raise TypeError(
            "Unknown option(s) for %s command: %s. "
            "Valid options are: %s."
            % (
                command_name,
                ", ".join(sorted(unknown_options)),
                ", ".join(sorted(valid_options)),
            )
        )
    # Move positional args out of options to mimic legacy optparse
    args = defaults.pop("args", ())
    if "skip_checks" not in options:
        defaults["skip_checks"] = True

    return command.execute(*args, **defaults)


class ManagementUtility:
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        if self.prog_name == "__main__.py":
            self.prog_name = "python -m esmerald"
        self.settings_exception = None

    def main_help_text(self, directives_only=False):
        """Return the script's main help text, as a string."""
        if directives_only:
            usage = sorted(get_directives())
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

            style = color_style()
            for app in sorted(directives_dict):
                usage.append("")
                usage.append(style.NOTICE("[%s]" % app))
                for name in sorted(directives_dict[app]):
                    usage.append("    %s" % name)
            # Output an extra note if settings are not properly configured
            if self.settings_exception is not None:
                usage.append(
                    style.NOTICE(
                        "Note that only Esmerald core directives are listed "
                        "as settings are not properly configured (error: %s)."
                        % self.settings_exception
                    )
                )

        return "\n".join(usage)

    def fetch_command(self, subdirective):
        """
        Try to fetch the given subdirective, printing a message with the
        appropriate command called from the command line (usually
        "esmerald-admin") if it can't be found.
        """
        # Get directives outside of try block to prevent swallowing exceptions
        directives = get_directives()
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

    def autocomplete(self):
        """
        Output completion suggestions for BASH.

        The output of this function is passed to BASH's `COMREPLY` variable and
        treated as completion suggestions. `COMREPLY` expects a space
        separated string as the result.

        The `COMP_WORDS` and `COMP_CWORD` BASH environment variables are used
        to get information about the cli input. Please refer to the BASH
        man-page for more information about this variables.

        Subcommand options are saved as pairs. A pair consists of
        the long option string (e.g. '--exclude') and a boolean
        value indicating if the option requires arguments. When printing to
        stdout, an equal sign is appended to options which require arguments.

        Note: If debugging this function, it is recommended to write the debug
        output in a separate file. Otherwise the debug output will be treated
        and formatted as potential completion suggestions.
        """
        # Don't complete if user hasn't sourced bash_completion file.
        if "ESMERALD_AUTO_COMPLETE" not in os.environ:
            return

        cwords = os.environ["COMP_WORDS"].split()[1:]
        cword = int(os.environ["COMP_CWORD"])

        try:
            curr = cwords[cword - 1]
        except IndexError:
            curr = ""

        subdirectives = [*get_directives(), "help"]
        options = [("--help", False)]

        # subdirective
        if cword == 1:
            print(" ".join(sorted(filter(lambda x: x.startswith(curr), subdirectives))))
        # subdirective options
        # special case: the 'help' subdirective has no options
        elif cwords[0] in subdirectives and cwords[0] != "help":
            subcommand_cls = self.fetch_command(cwords[0])
            # special case: add the names of installed apps to options
            parser = subcommand_cls.create_parser("", cwords[0])
            options.extend(
                (min(s_opt.option_strings), s_opt.nargs != 0)
                for s_opt in parser._actions
                if s_opt.option_strings
            )
            # filter out previously specified options from available options
            prev_opts = {x.split("=")[0] for x in cwords[1 : cword - 1]}
            options = (opt for opt in options if opt[0] not in prev_opts)

            # filter options by current input
            options = sorted((k, v) for k, v in options if k.startswith(curr))
            for opt_label, require_arg in options:
                # append '=' to options which require args
                if require_arg:
                    opt_label += "="
                print(opt_label)
        # Exit code of the bash completion function is never passed back to
        # the user, so it's safe to always exit with 0.
        # For more details see #25420.
        sys.exit(0)

    def execute(self):
        """
        Given the command-line arguments, figure out which subdirective is being
        run, create a parser appropriate to that command, and run it.
        """
        try:
            subdirective = self.argv[1]
        except IndexError:
            subdirective = "help"  # Display help if no arguments were given.

        # Preprocess options to extract --settings and --pythonpath.
        # These options could affect the directives that are available, so they
        # must be processed early.
        parser = DirectiveParser(
            prog=self.prog_name,
            usage="%(prog)s subdirective [options] [args]",
            add_help=False,
            allow_abbrev=False,
        )
        parser.add_argument("--pythonpath")
        parser.add_argument("args", nargs="*")  # catch-all
        try:
            options, args = parser.parse_known_args(self.argv[2:])
            handle_default_options(options)
        except DirectiveError:
            pass  # Ignore any option errors at this point.

        self.autocomplete()

        if subdirective == "help":
            if "--directives" in args:
                sys.stdout.write(self.main_help_text(directives_only=True) + "\n")
            elif not options.args:
                sys.stdout.write(self.main_help_text() + "\n")
            else:
                self.fetch_command(options.args[0]).print_help(self.prog_name, options.args[0])
        elif subdirective == "version" or self.argv[1:] == ["--version"]:
            sys.stdout.write(esmerald.__version__ + "\n")
        elif self.argv[1:] in (["--help"], ["-h"]):
            sys.stdout.write(self.main_help_text() + "\n")
        else:
            self.fetch_command(subdirective).run_from_argv(self.argv)


def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
