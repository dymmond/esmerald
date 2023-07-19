import os
import sys
import typing

from esmerald.conf import settings
from esmerald.core.directives.operations.shell.utils import import_objects
from esmerald.core.terminal import Print

printer = Print()


def vi_mode() -> typing.Any:
    editor = os.environ.get("EDITOR")
    if not editor:
        return False
    editor = os.path.basename(editor)
    return editor.startswith("vi") or editor.endswith("vim")


def get_ptpython(app: typing.Any, options: typing.Any = None) -> typing.Any:
    """Gets the PTPython shell.

    Loads the initial configurations from the main esmerald settings
    and boots up the kernel.
    """
    try:
        from ptpython.repl import embed, run_config

        def run_ptpython() -> None:
            imported_objects = import_objects(app)
            history_filename = os.path.expanduser("~/.ptpython_history")

            config_file = os.path.expanduser(settings.ptpython_config_file)
            if not os.path.exists(config_file):
                embed(
                    globals=imported_objects,
                    history_filename=history_filename,
                    vi_mode=vi_mode(),
                )
            else:
                embed(
                    globals=imported_objects,
                    history_filename=history_filename,
                    vi_mode=vi_mode(),
                    configure=run_config,
                )

    except (ModuleNotFoundError, ImportError):
        error = "You must have PTPython installed to run this. Run `pip install esmerald[ipython]`"
        printer.write_error(error)
        sys.exit(1)

    return run_ptpython
