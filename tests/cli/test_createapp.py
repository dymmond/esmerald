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


def _run_asserts():
    assert os.path.isfile("myapp/__init__.py") == True
    assert os.path.isfile("myapp/tests.py") == True
    assert os.path.isfile("myapp/v1/__init__.py") == True
    assert os.path.isfile("myapp/v1/schemas.py") == True
    assert os.path.isfile("myapp/v1/urls.py") == True
    assert os.path.isfile("myapp/v1/views.py") == True
    assert os.path.isfile("myapp/directives/__init__.py") == True
    assert os.path.isfile("myapp/directives/operations/__init__.py") == True


def test_create_app_with_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject")
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createapp myapp")

    _run_asserts()


def test_create_app_without_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject", is_app=True)
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createapp myapp", is_app=True)

    _run_asserts()


def test_create_app_without_env_var_with_app_flag(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject", is_app=True)
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd(
        "tests.cli.main:app", "esmerald --app tests.cli.main:app createapp myapp", is_app=True
    )

    _run_asserts()
