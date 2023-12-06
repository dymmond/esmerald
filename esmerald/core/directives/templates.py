import os
import shutil
import stat
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, Optional, Union

from jinja2 import Environment, FileSystemLoader

import esmerald
from esmerald.core.directives.base import BaseDirective
from esmerald.core.directives.exceptions import DirectiveError
from esmerald.core.terminal import Print

printer = Print()


class TemplateDirective(BaseDirective):
    """
    Copy either an Esmerald application layout template or an Esmerald project
    layout.
    """

    rewrite_template_suffixes: Any = (
        (".py-tpl", ".py"),
        (".e-tpl", ""),
    )

    def handle(self, app_or_project: str, name: str, **options: Any) -> Any:
        self.app_or_project = app_or_project
        self.name = name
        self.a_or_an = "an" if app_or_project == "app" else "a"
        self.verbosity = options["verbosity"]

        # Todo: Handle the creation of a simple project
        self.simple = options["simple"]

        self.validate_name(name)

        top_dir = os.path.join(os.getcwd(), name)
        try:
            os.makedirs(top_dir)
        except FileExistsError:
            raise DirectiveError(f"{top_dir} already exists.") from None
        except OSError as e:
            raise DirectiveError(detail=str(e)) from e

        base_name = f"{app_or_project}_name"
        base_subdir = f"{app_or_project}_template"

        context = {
            base_name: name,
            "esmerald_version": self.get_version(),
            "project_secret": options.get("secret_key"),
        }

        template_dir = os.path.join(esmerald.__path__[0], "conf", base_subdir)
        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):
            path_rest = root[prefix_length:]
            relative_dir = path_rest.replace(base_name, name)
            if relative_dir:
                target_dir = os.path.join(top_dir, relative_dir)
                os.makedirs(target_dir, exist_ok=True)

            for dirname in dirs[:]:
                if dirname.startswith(".") or dirname == "__pycache__":
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith((".pyo", ".pyc", ".py.class")):
                    continue

                old_path = os.path.join(root, filename)
                new_path = os.path.join(top_dir, relative_dir, filename.replace(base_name, name))
                project_dir = os.path.join(top_dir, relative_dir)
                template_name = filename
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path[: -len(old_suffix)] + new_suffix
                        template_name = template_name[: -len(old_suffix)] + new_suffix
                        break

                if os.path.exists(new_path):
                    raise DirectiveError(
                        "%s already exists. Overlaying %s %s into an existing "
                        "directory won't replace conflicting files."
                        % (
                            new_path,
                            self.a_or_an,
                            app_or_project,
                        )
                    )

                shutil.copyfile(old_path, new_path)
                if self.verbosity >= 2:
                    printer.write_info("Creating %s" % new_path)
                try:
                    self.manage_template_variables(template_name, new_path, project_dir, context)
                    self.apply_umask(old_path, new_path)
                    self.make_file_writable(new_path)
                except OSError:
                    printer.write_error(
                        "Notice: Couldn't set permission bits on %s. You're "
                        "probably using an uncommon filesystem setup. No "
                        "problem." % new_path,
                    )

    def manage_template_variables(
        self,
        template: Union[str, Path],
        destination: Union[str, Path],
        template_dir: Union[str, Path],
        context: Dict[str, Any],
    ) -> None:
        """
        Goes through every file generated and replaces the variables with the given
        context variables.
        """
        environment = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        template = environment.get_template(template)  # type: ignore
        rendered_template = template.render(context)  # type: ignore
        if os.path.isfile(destination):
            os.unlink(destination)
        with open(destination, "w") as f:
            f.write(rendered_template)

    def validate_name(self, name: Optional[str], name_or_dir: str = "name") -> None:
        if name is None:
            raise DirectiveError(
                "you must provide {an} {app} name".format(
                    an=self.a_or_an,
                    app=self.app_or_project,
                )
            )
        # Check it's a valid directory name.
        if not name.isidentifier():
            raise DirectiveError(
                "'{name}' is not a valid {app} {type}. Please make sure the "
                "{type} is a valid identifier.".format(
                    name=name,
                    app=self.app_or_project,
                    type=name_or_dir,
                )
            )
        try:
            import_module(name)
        except ImportError:
            pass
        else:
            raise DirectiveError(
                "'{name}' conflicts with the name of an existing Python "
                "module and cannot be used as {an} {app} {type}. Please try "
                "another {type}.".format(
                    name=name,
                    an=self.a_or_an,
                    app=self.app_or_project,
                    type=name_or_dir,
                )
            )

    def apply_umask(self, old_path: Union[str, Path], new_path: Union[str, Path]) -> None:
        current_umask = os.umask(0)
        os.umask(current_umask)
        current_mode = stat.S_IMODE(os.stat(old_path).st_mode)
        os.chmod(new_path, current_mode & ~current_umask)

    def make_file_writable(self, filename: str) -> None:
        """
        Make sure that the file is writeable.
        Useful if our source is read-only.
        """
        if not os.access(filename, os.W_OK):
            st = os.stat(filename)
            new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
            os.chmod(filename, new_permissions)
