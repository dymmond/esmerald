import os
import shutil

import pytest

from esmerald import Esmerald
from tests.cli.utils import run_cmd

app = Esmerald(routes=[])


@pytest.fixture(scope="module")
def create_folders():
    os.chdir(os.path.split(os.path.abspath(__file__))[0])
    try:
        os.remove("app.db")
    except OSError:
        pass
    try:
        shutil.rmtree("myproject")
    except OSError:
        pass
    try:
        shutil.rmtree("temp_folder")
    except OSError:
        pass

    yield

    try:
        os.remove("app.db")
    except OSError:
        pass
    try:
        shutil.rmtree("myproject")
    except OSError:
        pass
    try:
        shutil.rmtree("temp_folder")
    except OSError:
        pass


def test_create_project(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject")
    assert ss == 0

    with open("myproject/Makefile", "rt") as f:
        assert f.readline().strip() == ".DEFAULT_GOAL := help"
    with open("myproject/.gitignore", "rt") as f:
        assert f.readline().strip() == "# Byte-compiled / optimized / DLL files"
    with open("myproject/myproject/urls.py", "rt") as f:
        assert f.readline().strip() == '"""myproject Routes Configuration'


def _run_asserts():
    assert os.path.isfile("myproject/Makefile") == True
    assert os.path.isfile("myproject/.gitignore") == True
    assert os.path.isfile("myproject/myproject/__init__.py") == True
    assert os.path.isfile("myproject/myproject/main.py") == True
    assert os.path.isfile("myproject/myproject/serve.py") == True
    assert os.path.isfile("myproject/myproject/urls.py") == True
    assert os.path.isfile("myproject/myproject/tests/__init__.py") == True
    assert os.path.isfile("myproject/myproject/tests/test_app.py") == True
    assert os.path.isfile("myproject/myproject/configs/__init__.py") == True
    assert os.path.isfile("myproject/myproject/configs/settings.py") == True
    assert os.path.isfile("myproject/myproject/configs/development/__init__.py") == True
    assert os.path.isfile("myproject/myproject/configs/development/settings.py") == True
    assert os.path.isfile("myproject/myproject/configs/testing/__init__.py") == True
    assert os.path.isfile("myproject/myproject/configs/testing/settings.py") == True
    assert os.path.isfile("myproject/myproject/apps/__init__.py") == True


def test_create_project_files_with_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject")
    assert ss == 0

    _run_asserts()


def test_create_project_files_without_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject", is_app=True)
    assert ss == 0

    _run_asserts()


def test_create_project_files_without_env_var_and_with_app_flag(create_folders):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "esmerald --app tests.cli.main:app createproject myproject",
        is_app=True,
    )
    assert ss == 0

    _run_asserts()
