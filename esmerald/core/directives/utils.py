"""
Utils used by the Esmerald core management.
"""

import functools
import importlib
import os
import pkgutil
import sys
import typing
from difflib import get_close_matches
from importlib import import_module
from typing import Any, Optional

from esmerald.core.directives.base import BaseDirective
from esmerald.core.directives.exceptions import DirectiveError
from esmerald.core.terminal import Print

printer = Print()

IGNORE_FOLDERS = ["__pycache__"]
OPERATIONS = "operations"

EXCUDED_DIRECTIVES = ["list", "run"]


def find_directives(management_dir: str) -> typing.List[str]:
    """
    Shows the available directives from Esmerald.
    """
    directive_dir = os.path.join(management_dir, "operations")
    directive_list = []
    for _, name, is_package in pkgutil.iter_modules([directive_dir]):
        if not is_package and not name.startswith("_"):
            if name not in EXCUDED_DIRECTIVES:
                directive_list.append(name)
    return directive_list


def find_application_directives(
    management_dir: str,
) -> typing.Sequence[typing.Union[typing.Dict[Any, Any], str]]:
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
                directive_list.append({"name": name, "location": location.path})  # type: ignore
    return directive_list


def load_directive_class(app_name: str, name: str) -> Any:
    """
    Loads the directive class from native Esmerald.
    """
    module = import_module("{}.directives.operations.{}".format(app_name, name))
    return module.Directive()


def load_directive_class_by_filename(app_name: str, location: str) -> Any:
    """
    Loads the directive by filename.

    Passing a name a location, dynamically searches for the directive python file
    and loads it.
    """
    spec = importlib.util.spec_from_file_location(app_name, location)
    if not spec or spec is None:
        printer.write_error(f"{app_name} not found")
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Directive()


@functools.lru_cache(maxsize=None)
def get_directives(location: str) -> typing.Sequence[typing.Union[typing.Dict[Any, Any], str]]:
    command_list = find_directives(location)
    directives = []

    for name in command_list:
        directives.append({name: "esmerald.core", "location": None})
    return directives


@functools.lru_cache(maxsize=None)
def get_application_directives(
    location: str,
) -> typing.Sequence[typing.Dict[Any, Any]]:
    command_list = find_application_directives(location)
    directives = []

    for value in command_list:
        directives.append(
            {value["name"]: "application", "location": value["location"]}  # type: ignore
        )
    return directives


def fetch_custom_directive(subdirective: Any, location: Optional[str]) -> Any:
    """Fetches the directive classes custom and native"""
    directives = get_application_directives(location)

    counter = 0
    matches = []
    app_name = None

    for directive in sorted(directives, key=lambda d: d["location"]):
        try:
            for key, _ in directive.items():
                if key == subdirective:
                    app_name = key
                    location = directive["location"]
                    break
        except KeyError:
            counter += 1
            directive = {k: v for k, v in directive.items() if k != "location"}
            matches.extend(get_close_matches(subdirective, directive))

            if matches and len(directives) == counter:
                printer.write_error("Did you mean %s?" % matches[0])

            if len(directives) == counter:
                return None
            continue

    if not app_name:
        directive = {k: v for k, v in directive.items() if k != "location"}
        matches.extend(get_close_matches(subdirective, directive))

        if matches:
            printer.write_error("Did you mean %s?" % matches[0])
            return None
        return None

    name = f"{location}/{app_name}.py"
    klass = load_directive_class_by_filename(app_name, name)

    if not isinstance(klass, BaseDirective):
        raise DirectiveError(detail="The directive must be a subclass of BaseDirective")
    return klass


def fetch_directive(subdirective: Any, location: Optional[str], is_custom: bool = False) -> Any:
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

            directive = {k: v for k, v in directive.items() if k != "location"}  # type: ignore
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
