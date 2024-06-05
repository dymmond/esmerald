import os
import shutil
import subprocess
import click
from http.server import HTTPServer, SimpleHTTPRequestHandler
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, List

import mkdocs.commands.build
import mkdocs.commands.serve
import mkdocs.config
import mkdocs.utils


import yaml


mkdocs_name = "mkdocs.yml"

missing_translation_snippet = """
{!../../../docs/missing-translation.md!}
"""

docs_path = Path("docs")
en_docs_path = Path("docs/en")
en_config_path: Path = en_docs_path / mkdocs_name
site_path = Path("site").absolute()
build_site_path = Path("site_build").absolute()


@click.group()
def cli():
    pass


def get_en_config() -> Dict[str, Any]:
    return mkdocs.utils.yaml_load(en_config_path.read_text(encoding="utf-8"))


def get_lang_paths() -> List[Path]:
    return sorted(docs_path.iterdir())


def complete_existing_lang(incomplete: str):
    lang_path: Path
    for lang_path in get_lang_paths():
        if lang_path.is_dir() and lang_path.name.startswith(incomplete):
            yield lang_path.name


def get_updated_config_content() -> Dict[str, Any]:
    config = get_en_config()
    languages = [{"en": "/"}]
    new_alternate: List[Dict[str, str]] = []
    # Language names sourced from https://quickref.me/iso-639-1
    # Contributors may wish to update or change these, e.g. to fix capitalization.
    language_names_path = Path(__file__).parent / "../docs/language_names.yml"
    local_language_names: Dict[str, str] = mkdocs.utils.yaml_load(
        language_names_path.read_text(encoding="utf-8")
    )
    for lang_path in get_lang_paths():
        if lang_path.name in {"en", "em"} or not lang_path.is_dir():
            continue
        code = lang_path.name
        languages.append({code: f"/{code}/"})
    for lang_dict in languages:
        code = list(lang_dict.keys())[0]
        url = lang_dict[code]
        if code not in local_language_names:
            print(
                f"Missing language name for: {code}, "
                "update it in docs/language_names.yml"
            )
            raise click.Abort()
        use_name = f"{code} - {local_language_names[code]}"
        new_alternate.append({"link": url, "name": use_name})
    new_alternate.append({"link": "/em/", "name": "😉"})
    config["extra"]["alternate"] = new_alternate
    return config


def update_config() -> None:
    config = get_updated_config_content()
    en_config_path.write_text(
        yaml.dump(config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )


def build_site(lang: str = "en") -> None:
    config_file_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", lang, "mkdocs.yml")
    )
    subprocess.run(["mkdocs", "build", "-f", config_file_path], check=True)



# def build_language(lang: str = "en") -> None:
#     config_file_path = os.path.abspath(
#         os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", lang, "mkdocs.yml")
#     )
#     lang_path: Path = Path(f"docs/{lang}")
#
#     if not lang_path.is_dir():
#         click.echo(f"The language translation doesn't seem to exist yet: {lang}")
#         raise click.Abort()
#     click.echo(f"Building docs for: {lang}")
#     build_site_dist_path = build_site_path / lang
#     if lang == "en":
#         dist_path = site_path
#     else:
#         dist_path = site_path / lang
#         shutil.rmtree(dist_path, ignore_errors=True)
#     current_dir = os.getcwd()
#     os.chdir(lang_path)
#     shutil.rmtree(build_site_dist_path, ignore_errors=True)
#     # subprocess.run(["mkdocs", "build", "--site-dir", build_site_dist_path], check=True)
#
#     subprocess.run(["mkdocs", "build", "-f", config_file_path, "--site-dir", build_site_dist_path], check=True)
#
#     shutil.copytree(build_site_dist_path, dist_path, dirs_exist_ok=True)
#     os.chdir(current_dir)
#     click.echo(click.style(f"Successfully built docs for: {lang}", fg="green"))


@cli.command()
@click.option("-l", "--lang")
def new_lang(lang: str):
    """
    Generate a new docs translation directory for the language LANG.
    """
    new_path: Path = Path("docs") / lang
    if new_path.exists():
        click.echo(f"The language was already created: {lang}")
        raise click.Abort()
    new_path.mkdir()
    new_config_path: Path = Path(new_path) / mkdocs_name
    new_config_path.write_text(
        f"INHERIT: ../en/mkdocs.yml\nsite_dir: '../../site/{lang}'\n",
        encoding="utf-8"
    )
    new_config_docs_path: Path = new_path / "docs"
    new_config_docs_path.mkdir()
    en_index_path: Path = en_docs_path / "docs" / "index.md"
    new_index_path: Path = new_config_docs_path / "index.md"
    en_index_content = en_index_path.read_text(encoding="utf-8")
    new_index_content = f"{missing_translation_snippet}\n\n{en_index_content}"
    new_index_path.write_text(new_index_content, encoding="utf-8")
    click.echo(click.style(f"Successfully initialized: {new_path}", fg="green"))
    update_languages()


@cli.command()
@click.option("--lang", "-l", default="en")
def build_lang(lang: str) -> None:
    """
    Build the docs for a language.
    """
    # build_language(lang)
    build_site(lang)


@cli.command()
def build_all() -> None:
    """
    Build mkdocs site for en, and then build each language inside, end result is located
    at directory ./site/ with each language inside.
    """
    shutil.rmtree(site_path, ignore_errors=True)
    langs = [lang.name for lang in get_lang_paths() if lang.is_dir()]
    cpu_count = os.cpu_count() or 1
    process_pool_size = cpu_count
    click.echo(f"Using process pool size: {process_pool_size}")
    for lang in langs:
        build_site(lang)
    # with Pool(process_pool_size) as p:
    #     p.map(build_lang, langs)


@cli.command()
def update_languages() -> None:
    """
    Update the mkdocs.yml file Languages section including all the available languages.
    """
    update_config()


@cli.command()
def serve() -> None:
    """
    A quick server to preview a built site with translations.
    For development, prefer the command live (or just mkdocs serve).
    This is here only to preview a site with translations already built.
    Make sure you run the build-all command first.
    """
    click.echo("Warning: this is a very simple server.")
    click.echo("For development, use the command live instead.")
    click.echo("This is here only to preview a site with translations already built.")
    click.echo("Make sure you run the build-all command first.")
    os.chdir("site")
    server_address = ("", 8000)
    server = HTTPServer(server_address, SimpleHTTPRequestHandler)
    click.echo("Serving at: http://127.0.0.1:8000")
    server.serve_forever()


@cli.command()
@click.option("-l", "--lang", default="en", help='lang')
def live(lang: str) -> None:
    """
    Serve with livereload a docs site for a specific language.

    This only shows the actual translated files, not the placeholders created with
    build-all.

    Takes an optional LANG argument with the name of the language to serve, by default en.
    """
    click.echo("Warning: this is a very simple server.")
    lang_path: Path = docs_path / lang
    os.chdir(lang_path)
    mkdocs.commands.serve.serve(dev_addr="127.0.0.1:8000")


@cli.command()
def verify_config() -> None:
    """
    Verify main mkdocs.yml content to make sure it uses the latest language names.
    """
    click.echo("Verifying mkdocs.yml")
    config = get_en_config()
    updated_config = get_updated_config_content()
    if config != updated_config:
        click.secho(click.style(
            f"docs/en/mkdocs.yml outdated from docs/language_names.yml, "
            "update language_names.yml and run "
            "python ./scripts/docs.py update-languages",
            fg="red")
        )
        raise click.Abort()
    click.echo("Valid mkdocs.yml ✅")


if __name__ == '__main__':
    cli()
