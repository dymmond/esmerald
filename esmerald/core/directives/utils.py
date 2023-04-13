"""
Utils used by the Esmerald core management.
"""
import functools
import os
import pkgutil
import sys
import typing
from difflib import get_close_matches
from importlib import import_module
from typing import Any

from esmerald.core.directives.base import BaseDirective
from esmerald.core.terminal import Print

printer = Print()

IGNORE_FOLDERS = ["__pycache__"]
OPERATIONS = "operations"


def find_directives(management_dir: str) -> typing.List[str]:
    """
    Shows the available directives from Esmerald.
    """
    directive_dir = os.path.join(management_dir, "operations")
    directive_list = []
    for _, name, is_package in pkgutil.iter_modules([directive_dir]):
        if not is_package and not name.startswith("_"):
            directive_list.append(name)
    return directive_list


def find_application_directives(management_dir: str) -> typing.List[str]:
    """
    Iterates through the application tree and finds the directives available
    to run.
    """
    directive_list = []
    for root, folders, _ in os.walk(management_dir):
        if OPERATIONS not in folders:
            continue

        directive_dir = os.path.join(root, "operations")
        for location, name, is_package in pkgutil.iter_modules([directive_dir]):
            if not is_package and not name.startswith("_"):
                directive_list.append({"name": name, "location": location.path})
    return directive_list


def load_directive_class(app_name: str, name: str) -> Any:
    module = import_module("%s.directives.operations.%s" % (app_name, name))
    return module.Directive()


def load_directive_class_by_filename(app_name: str, name: str) -> Any:
    module = import_module("%s.directives.operations.%s" % (app_name, name))
    return module.Directive()


@functools.lru_cache(maxsize=None)
def get_directives(location: str) -> typing.List[str]:
    command_list = find_directives(location)
    directives = []

    for name in command_list:
        directives.append({name: "esmerald.core", "location": None})
    return directives


@functools.lru_cache(maxsize=None)
def get_application_directives(location: str) -> typing.List[str]:
    command_list = find_application_directives(location)
    directives = []

    for value in command_list:
        directives.append({value["name"]: "application", "location": value["location"]})
    return directives


def fetch_custom_directive(subdirective: Any, location: str) -> Any:
    """Fetches the directive classes custom and native"""
    directives = get_application_directives(location)

    counter = 0
    matches = []

    for directive in directives:
        try:
            app_name = directive[subdirective]
        except KeyError:
            counter += 1

            directive = {k: v for k, v in directive.items() if k != "location"}
            matches.extend(get_close_matches(subdirective, directive))

            if matches and len(directives) == counter:
                printer.write_error("Did you mean %s?" % matches[0])

            if len(directives) == counter:
                return None
            continue

    if isinstance(app_name, BaseDirective):
        klass = app_name
    else:
        klass = load_directive_class_by_filename(app_name, subdirective)
    return klass


def fetch_directive(subdirective: Any, location: str, is_custom: bool = False) -> Any:
    """Fetches the directive classes custom and native"""
    if not is_custom:
        directives = get_directives(location)
    else:
        return fetch_custom_directive(subdirective, location)

    counter = 0
    matches = []

    for directive in directives:
        try:
            app_name = directive[subdirective]
        except KeyError:
            counter += 1

            directive = {k: v for k, v in directive.items() if k != "location"}
            matches.extend(get_close_matches(subdirective, directive))

            if matches and len(directives) == counter:
                printer.write_error("Did you mean %s?" % matches[0])

            if len(directives) == counter:
                return None
            continue

    if isinstance(app_name, BaseDirective):
        klass = app_name
    else:
        klass = load_directive_class(app_name, subdirective)
    return klass
