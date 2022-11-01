"""
Template based from Django as it handles really well with Directives
and it is fully supported by their systems.

Esmerald readapted the same concept to allow a simple integration for the
`esmerald-admin` allowing the creation of a project and app via command line.
"""
import argparse
import os
import shutil
import stat
import tempfile
from importlib import import_module
from typing import Any, Dict, Optional, Union

import esmerald
from esmerald.core import archive
from esmerald.core.management.base import BaseDirective, DirectiveError
from jinja2 import Environment, FileSystemLoader
from pydantic import FilePath


class TemplateCommand(BaseDirective):
    """
    Copy either an Esmerald application layout template or an Esmerald project
    layout.
    """

    url_schemes = ["http", "https", "ftp"]

    rewrite_template_suffixes = (
        # Allow shipping invalid .py files without byte-compilation.
        (".py-tpl", ".py"),
        (".e-tpl", ""),
    )

    def add_arguments(self, parser: Any):
        parser.add_argument("name", help="Name of the application or project.")
        parser.add_argument("directory", nargs="?", help="Optional destination directory")
        parser.add_argument("--template", help="The path or URL to load the template from.")
        parser.add_argument(
            "--name",
            "-n",
            dest="files",
            action="append",
            default=[],
            help="The file name(s) to render. Separate multiple file names "
            "with commas, or use -n multiple times.",
        )
        parser.add_argument(
            "--exclude",
            "-x",
            action="append",
            default=argparse.SUPPRESS,
            nargs="?",
            const="",
            help=(
                "The directory name(s) to exclude, in addition to .git and "
                "__pycache__. Can be used multiple times."
            ),
        )

    def handle(
        self,
        app_or_project: str,
        name: str,
        target: Optional[Any] = None,
        **options: Dict[str, Any],
    ):
        self.app_or_project = app_or_project
        self.a_or_an = "an" if app_or_project == "app" else "a"
        self.paths_to_remove = []
        self.verbosity = options["verbosity"]

        self.validate_name(name)

        if target is None:
            top_dir = os.path.join(os.getcwd(), name)
            try:
                os.makedirs(top_dir)
            except FileExistsError:
                raise DirectiveError(f"{top_dir} already exists.")
            except OSError as e:
                raise DirectiveError(e)
        else:
            top_dir = os.path.abspath(os.path.expanduser(target))
            if app_or_project == "app":
                self.validatate_name(os.path.basename(top_dir), "directory")
            if not os.path.exists(top_dir):
                raise DirectiveError(
                    f"Destination directory {top_dir} does not " "exist, please create it first."
                )

        base_name = f"{app_or_project}_name"
        base_subdir = f"{app_or_project}_template"

        context = {
            base_name: name,
            "esmerald_version": self.get_version(),
            "project_secret": options.get("secret_key"),
        }

        template_dir = self.handle_template(options["template"], base_subdir)
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
                    # Ignore some files as they cause various breakages.
                    continue
                old_path = os.path.join(root, filename)
                new_path = os.path.join(top_dir, relative_dir, filename.replace(base_name, name))
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path[: -len(old_suffix)] + new_suffix
                        break  # Only rewrite once

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
                # Only render the Python files, as we don't want to
                # accidentally render Esmerald templates files
                shutil.copyfile(old_path, new_path)

                if self.verbosity >= 2:
                    self.stdout.write("Creating %s" % new_path)
                try:
                    self.manage_template_variables(new_path, new_path, "/", context)
                    self.apply_umask(old_path, new_path)
                    self.make_file_writable(new_path)
                except OSError:
                    self.stderr.write(
                        "Notice: Couldn't set permission bits on %s. You're "
                        "probably using an uncommon filesystem setup. No "
                        "problem." % new_path,
                        self.style.NOTICE,
                    )

    def manage_template_variables(
        self,
        template: Union[str, FilePath],
        destination: Union[str, FilePath],
        template_dir: Union[str, FilePath],
        context: Dict[str, Any],
    ):
        """
        Goes through every file generated and replaces the project_name with the given
        project name from the command line.
        """
        environment = Environment(loader=FileSystemLoader(template_dir))
        template = environment.get_template(template)
        rendered_template = template.render(context)
        if os.path.isfile(destination):
            os.unlink(destination)
        with open(destination, "w") as f:
            f.write(rendered_template)

    def handle_template(self, template: Union[str, FilePath], subdir: Union[str, FilePath]):
        """
        Determine where the app or project templates are.
        Use esmerald.__path__[0] as the default because the Esmerald install
        directory isn't known.
        """
        if template is None:
            return os.path.join(esmerald.__path__[0], "conf", subdir)
        else:
            if template.startswith("file://"):
                template = template[7:]
            expanded_template = os.path.expanduser(template)
            expanded_template = os.path.normpath(expanded_template)
            if os.path.isdir(expanded_template):
                return expanded_template

            absolute_path = os.path.abspath(expanded_template)
            if os.path.exists(absolute_path):
                return self.extract(absolute_path)

        raise DirectiveError("couldn't handle %s template %s." % (self.app_or_project, template))

    def validate_name(self, name, name_or_dir="name"):
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
        # Check it cannot be imported.
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

    def extract(self, filename: str):
        """
        Extract the given file to a temporary directory and return
        the path of the directory with the extracted content.
        """
        prefix = "esmerald_%s_template_" % self.app_or_project
        tempdir = tempfile.mkdtemp(prefix=prefix, suffix="_extract")
        self.paths_to_remove.append(tempdir)
        if self.verbosity >= 2:
            self.stdout.write("Extracting %s" % filename)
        try:
            archive.extract(filename, tempdir)
            return tempdir
        except (archive.ArchiveException, OSError) as e:
            raise DirectiveError("couldn't extract file %s to %s: %s" % (filename, tempdir, e))

    def apply_umask(self, old_path: Union[str, FilePath], new_path: Union[str, FilePath]):
        current_umask = os.umask(0)
        os.umask(current_umask)
        current_mode = stat.S_IMODE(os.stat(old_path).st_mode)
        os.chmod(new_path, current_mode & ~current_umask)

    def make_file_writable(self, filename: str):
        """
        Make sure that the file is writeable.
        Useful if our source is read-only.
        """
        if not os.access(filename, os.W_OK):
            st = os.stat(filename)
            new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
            os.chmod(filename, new_permissions)
