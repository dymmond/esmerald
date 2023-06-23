import os
import sys
import typing
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

from esmerald import ChildEsmerald, Esmerald
from esmerald.core.directives.constants import (
    DISCOVERY_FILES,
    DISCOVERY_FUNCTIONS,
    ESMERALD_DISCOVER_APP,
)
from esmerald.core.terminal import Print

printer = Print()


@dataclass
class Scaffold:
    """
    Simple Application scaffold that holds the
    information about the app and the path to
    the same app.
    """

    path: str
    app: typing.Union[Esmerald, ChildEsmerald]


@dataclass
class DirectiveEnv:
    """
    Loads an arbitraty application into the object
    and returns the App.
    """

    path: typing.Optional[str] = None
    app: typing.Optional[typing.Union[Esmerald, ChildEsmerald]] = None
    command_path: typing.Optional[str] = None

    def load_from_env(self, path: typing.Optional[str] = None) -> "DirectiveEnv":
        """
        Loads the environment variables into the scaffold.
        """
        # Adds the current path where the command is being invoked
        # To the system path
        cwd = Path().cwd()
        command_path = str(cwd)
        if command_path not in sys.path:
            sys.path.append(command_path)
        try:
            import dotenv

            dotenv.load_dotenv()
        except ImportError:
            ...

        _path = os.getenv(ESMERALD_DISCOVER_APP) if not path else path
        _app = self.find_app(path=_path, cwd=cwd)

        return DirectiveEnv(path=_app.path, app=_app.app, command_path=command_path)

    def import_app_from_string(cls, path: typing.Optional[str] = None) -> Scaffold:
        if path is None:
            raise OSError(
                "Path cannot be None. Set env `ESMERALD_DEFAULT_APP` or use `--app` instead."
            )
        module_str_path, app_name = path.split(":")
        module = import_module(module_str_path)
        app = getattr(module, app_name)
        return Scaffold(path=path, app=app)

    def _get_folders(self, path: Path) -> typing.List[str]:
        """
        Lists all the folders and checks if there is any file from the DISCOVERY_FILES available
        """
        return [directory.path for directory in os.scandir(path) if directory.is_dir()]

    def _find_app_in_folder(self, path: Path, cwd: Path) -> typing.Union[Scaffold, None]:
        """
        Iterates inside the folder and looks up to the DISCOVERY_FILES.
        """
        for discovery_file in DISCOVERY_FILES:
            filename = f"{str(path)}/{discovery_file}"
            if not os.path.exists(filename):
                continue

            file_path = path / discovery_file
            dotted_path = ".".join(file_path.relative_to(cwd).with_suffix("").parts)

            # Load file from module
            module = import_module(dotted_path)

            # Iterates through the elements of the module.
            for attr, value in module.__dict__.items():
                if isinstance(value, Esmerald):
                    app_path = f"{dotted_path}:{attr}"
                    return Scaffold(app=value, path=app_path)

            # Iterate over default pattern application functions
            for func in DISCOVERY_FUNCTIONS:
                if hasattr(module, func):
                    app_path = f"{dotted_path}:{func}"
                    fn = getattr(module, func)
                    return Scaffold(app=fn(), path=app_path)
        return None

    def find_app(self, path: typing.Optional[str], cwd: Path) -> Scaffold:
        """
        Loads the application based on the path provided via env var.

        If no --app is provided, goes into auto discovery up to one level.
        """

        if path:
            return self.import_app_from_string(path)

        scaffold: typing.Union[Scaffold, None] = None

        # Check current folder
        scaffold = self._find_app_in_folder(cwd, cwd)
        if scaffold:
            return scaffold

        # Goes into auto discovery mode for one level, only.
        folders = self._get_folders(cwd)

        for folder in folders:
            folder_path = cwd / folder
            scaffold = self._find_app_in_folder(folder_path, cwd)

            if not scaffold:
                continue
            break

        if not scaffold:
            raise OSError("Could not find an Esmerald application.")

        return scaffold
