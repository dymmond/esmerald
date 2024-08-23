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
    assert os.path.isfile("myapp/__init__.py") is True
    assert os.path.isfile("myapp/tests.py") is True
    assert os.path.isfile("myapp/dtos.py") is True
    assert os.path.isfile("myapp/urls.py") is True
    assert os.path.isfile("myapp/controllers.py") is True
    assert os.path.isfile("myapp/repository.py") is True
    assert os.path.isfile("myapp/service.py") is True
    assert os.path.isfile("myapp/directives/__init__.py") is True
    assert os.path.isfile("myapp/directives/operations/__init__.py") is True


def test_create_app_with_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject")
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createapp myapp --context")

    _run_asserts()


def test_create_app_without_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject", is_app=False)
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createapp myapp --context", is_app=False)

    _run_asserts()


def test_create_app_without_env_var_with_app_flag(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject", is_app=False)
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd(
        "tests.cli.main:app", "esmerald --app tests.cli.main:app createapp myapp --context", is_app=False
    )

    _run_asserts()
