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
from django.template import Context, Engine
from esmerald.conf import settings
from esmerald.core.management.base import BaseCommand, CommandError
from esmerald.core.management.context import Context
from esmerald.core.management.utils import (
    find_formatters,
    handle_extensions,
    run_formatters,
)


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

        if target is None:
            top_dir = os.path.join(os, os.getcwd(), name)
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

        # Find formatters, which are external executables, before input
        # from the templates can sneak into the path.
        formatter_paths = find_formatters()

        extensions = tuple(handle_extensions(options["extensions"]))
        extra_files = []
        excluded_directories = [".git", "__pycache__"]

        for file in options["files"]:
            extra_files.extend(map(lambda x: x.strip(), file.split(",")))

        if self.verbosity >= 2:
            self.stdout.write(
                f"Rendering {app_or_project} template files with extensions: {', '.join(extensions)}"
            )
            self.stdout.write(
                f'Rendering {app_or_project} template files with filenames: {', '.join(extra_files)}'
            )

        base_name = f'{app_or_project}_name'
        base_subdir = f'{app_or_project}_template'
        base_directory = f'{app_or_project}_directory'
        camel_case_name = f'camel_case_{app_or_project}_name'
        camel_case_value = ''.join(x for x in name.title() if x != '_')

        context = Context({
            **options,
            base_name: name,
            base_directory: top_dir,
            camel_case_name: camel_case_value,
            'esmerald_version': esmerald.__version__
        }, autoescape=True)

        template_dir = self.handle_template(options['template'], base_subdir)
        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):
            path_rest = root[prefix_length:]
            relative_dir = path_rest.replace(base_name, name)
            if relative_dir:
                target_dir = os.path.join(top_dir, relative_dir)
                os.makedirs(target_dir, exist_ok=True)

            for dirname in dirs[:]:
                if dirname.startswith('.') or dirname == '__pycache__':
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith(('.pyo', '.pyc', '.py.class')):
                    # Ignore some files as they cause various breakages.
                    continue
                old_path = os.path.join(root, filename)
                new_path = os.path.join(
                    top_dir, relative_dir, filename.replace(base_name, name)
                )
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path[:-len(old_suffix)] + new_suffix
                        break  # Only rewrite once

                if os.path.exists(new_path):
                    raise CommandError(
                        "%s already exists. Overlaying %s %s into an existing "
                        "directory won't replace conflicting files." % (
                            new_path, self.a_or_an, app_or_project,
                        )
                    )

                # Only render the Python files, as we don't want to
                # accidentally render Esmerald templates files
                if new_path.endswith(extensions) or filename in extra_files:
                    with open(old_path, encoding='utf-8') as template_file:
                        content = template_file.read()
                    template = Engine().from_string(content)
                    content = template.render(context)
                    with open(new_path, 'w', encoding='utf-8') as new_file:
                        new_file.write(content)
                else:
                    shutil.copyfile(old_path, new_path)

                if self.verbosity >= 2:
                    self.stdout.write('Creating %s' % new_path)
                try:
                    shutil.copymode(old_path, new_path)
                    self.make_writeable(new_path)
                except OSError:
                    self.stderr.write(
                        "Notice: Couldn't set permission bits on %s. You're "
                        "probably using an uncommon filesystem setup. No "
                        "problem." % new_path, self.style.NOTICE)


