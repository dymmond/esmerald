"""
Utils used by the Esmerald core management.
"""
import functools
import os
import pkgutil
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from esmerald.core.management.typing import DirectiveType


def find_directives(management_dir):
    directive_dir = os.path.join(management_dir, "directives")
    directive_list = []
    for _, name, is_package in pkgutil.iter_modules([directive_dir]):
        if not is_package and not name.startswith("_"):
            directive_list.append(name)
    return directive_list


def load_directive_class(app_name: str, name: str) -> "DirectiveType":
    module = import_module("%s.management.directives.%s" % (app_name, name))
    return module.Directive()


@functools.lru_cache(maxsize=None)
def get_directives(location):
    command_list = find_directives(location)
    directives = {name: "esmerald.core" for name in command_list}

    return directives
