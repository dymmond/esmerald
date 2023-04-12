"""
Utils used by the Esmerald core management.
"""
import functools
import os
import pkgutil
import typing
from importlib import import_module
from typing import TYPE_CHECKING, Any


def find_directives(management_dir):
    directive_dir = os.path.join(management_dir, "operations")
    directive_list = []
    for _, name, is_package in pkgutil.iter_modules([directive_dir]):
        if not is_package and not name.startswith("_"):
            directive_list.append(name)
    return directive_list


def load_directive_class(app_name: str, name: str) -> Any:
    module = import_module("%s.directives.operations.%s" % (app_name, name))
    return module.Directive()


@functools.lru_cache(maxsize=None)
def get_directives(location: str) -> typing.List[str]:
    command_list = find_directives(location)
    directives = {name: "esmerald.core" for name in command_list}
    return directives
