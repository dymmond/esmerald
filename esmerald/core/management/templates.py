import argparse
import mimetypes
import os
import posixpath
import shutil
import stat
import tempfile
from importlib import import_module
from typing import Any, Dict, List, Optional
from urllib.request import build_opener

import esmerald
import ipdb
from django.template import Context, Engine
from esmerald.conf import settings
from esmerald.core.management.base import BaseCommand, CommandError
from esmerald.core.management.context import Context


class TemplateCommand(BaseCommand):
    """
    Copy wither an Esmerald application layout template or an Esmerald project
    layout.
    """

    url_schemes = ["http", "https", "ftp"]

    rewrite_template_suffixes = (
        # Allow shipping invalid .py files without byte-compilation.
        (".py-tpl", ".py"),
    )

    def add_arguments(self, parser: Any):
        parser.add_argument("name", help="Name of the application or project.")
        parser.add_argument(
            "directory", nargs="?", help="Optional destination directory"
        )
        parser.add_argument(
            "--template", help="The path or URL to load the template from."
        )
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
        ipdb.sset_trace()

        if target is None:
            top_dir = os.path.join(os.getcwd(), name)
            try:
                os.makedirs(top_dir)
            except FileExistsError:
                raise CommandError(f"{top_dir} already exists.")
            except OSError as e:
                raise CommandError(e)
        else:
            top_dir = os.path.abspath(os.path.expanduser(target))
            if app_or_project == "app":
                self.validatate_name(os.path.basename(top_dir), "directory")
            if not os.path.exists(top_dir):
                raise CommandError(
                    f"Destination directory {top_dir} does not "
                    "exist, please create it first."
                )

    def handle_template(self, template, subdir):
        """
        Determine where the app or project templates are.
        Use django.__path__[0] as the default because the Django install
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
            if self.is_url(template):
                # downloads the file and returns the path
                absolute_path = self.download(template)
            else:
                absolute_path = os.path.abspath(expanded_template)
            if os.path.exists(absolute_path):
                return self.extract(absolute_path)

        raise CommandError(
            "couldn't handle %s template %s." % (self.app_or_project, template)
        )

    def validate_name(self, name, name_or_dir="name"):
        if name is None:
            raise CommandError(
                "you must provide {an} {app} name".format(
                    an=self.a_or_an,
                    app=self.app_or_project,
                )
            )
        # Check it's a valid directory name.
        if not name.isidentifier():
            raise CommandError(
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
            raise CommandError(
                "'{name}' conflicts with the name of an existing Python "
                "module and cannot be used as {an} {app} {type}. Please try "
                "another {type}.".format(
                    name=name,
                    an=self.a_or_an,
                    app=self.app_or_project,
                    type=name_or_dir,
                )
            )
