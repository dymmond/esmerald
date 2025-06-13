import os
import sys
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

from esmerald import ChildEsmerald, Esmerald
from esmerald.core.directives.constants import (
    DISCOVERY_ATTRS,
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
    app: Esmerald | ChildEsmerald
    app_location: Path | None = None
    discovery_file: str | None = None


@dataclass
class ModuleInfo:
    module_import: list[str] | None = None
    extra_sys_path: Path | None = None
    module_paths: list[Path] | None = None
    discovery_file: str | None = None


@dataclass
class DirectiveEnv:
    """
    Loads an arbitrary application into the object
    and returns the App.
    """

    path: str | None = None
    app: Esmerald | ChildEsmerald | None = None
    command_path: str | None = None
    module_info: ModuleInfo | None = None

    def load_from_env(self, path: str | None = None) -> "DirectiveEnv":
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

        return DirectiveEnv(
            path=_app.path,
            app=_app.app,
            command_path=command_path,
            module_info=self.get_module_data_from_path(
                _app.app_location, _app.path, _app.discovery_file
            ),
        )

    def get_module_data_from_path(
        self, path: Path, module_import: str, discovery_file: str
    ) -> ModuleInfo:
        """
        Returns the module information based on the path provided.
        It resolves the path, checks if it is a file or a directory,
        and constructs the module import path accordingly.
        If the path is a file, it checks if it is an `__init__.py` file
        and adjusts the module paths accordingly.
        If the path is a directory, it checks for the presence of `__init__.py`
        files in the parent directories to construct the module paths.
        """
        if not path:
            return ModuleInfo()

        use_path = path.resolve()
        module_path = use_path
        if use_path.is_file() and use_path.stem == "__init__":
            module_path = use_path.parent

        module_paths = [module_path]
        extra_sys_path = module_path.parent

        initial_init = module_path / "__init__.py"
        if initial_init.is_file() and initial_init.stem == "__init__":
            module_paths.insert(0, module_path.parent)
            extra_sys_path = module_path.parent.parent

        for parent in module_path.parents:
            init_path = parent / "__init__.py"
            if init_path.is_file():
                module_paths.insert(0, parent)
                extra_sys_path = parent.parent
            else:
                break

        split_module = module_import.split(":")
        return ModuleInfo(
            module_import=split_module,
            extra_sys_path=extra_sys_path.resolve(),
            module_paths=module_paths,
            discovery_file=discovery_file,
        )

    def import_app_from_string(cls, path: str | None = None) -> Scaffold:
        if path is None:
            raise OSError(
                "Path cannot be None. Set env `ESMERALD_DEFAULT_APP` or use `--app` instead."
            )
        module_str_path, app_name = path.split(":")
        module = import_module(module_str_path)
        app = getattr(module, app_name)
        return Scaffold(path=path, app=app)

    def _get_folders(self, path: Path) -> list[str]:
        """
        Lists all the folders and checks if there is any file from the DISCOVERY_FILES available
        """
        return [directory.path for directory in os.scandir(path) if directory.is_dir()]

    def _find_app_in_folder(self, path: Path, cwd: Path) -> Scaffold | None:
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

            # FIrst check some attrs
            for attr in DISCOVERY_ATTRS:
                value = getattr(module, attr, None)
                if value:
                    app_path = f"{dotted_path}:{attr}"
                    return Scaffold(
                        app=value,
                        path=app_path,
                        app_location=path,
                        discovery_file=discovery_file,
                    )

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
                    return Scaffold(
                        app=fn(),
                        path=app_path,
                        app_location=path,
                        discovery_file=discovery_file,
                    )
        return None

    def find_app(self, path: str | None, cwd: Path) -> Scaffold:
        """
        Loads the application based on the path provided via env var.

        If no --app is provided, goes into auto discovery up to one level.
        """

        if path:
            return self.import_app_from_string(path)

        # Check current folder
        scaffold: Scaffold | None = self._find_app_in_folder(cwd, cwd)
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
