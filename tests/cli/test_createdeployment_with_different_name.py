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
    assert os.path.isfile("deploy/docker/Dockerfile") is True
    assert os.path.isfile("deploy/gunicorn/gunicorn_conf.py") is True
    assert os.path.isfile("deploy/nginx/nginx.conf") is True
    assert os.path.isfile("deploy/nginx/nginx.json-logging.conf") is True
    assert os.path.isfile("deploy/supervisor/supervisord.conf") is True


def test_create_app_with_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject")
    assert ss == 0

    os.chdir("myproject")

    (o, e, ss) = run_cmd(
        "tests.cli.main:app", "esmerald createdeployment myproject --deployment-folder-name deploy"
    )

    _run_asserts()


def test_create_app_without_env_var(create_folders):
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject", is_app=False)
    assert ss == 0

    os.chdir("myproject")

    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "esmerald createdeployment myproject --deployment-folder-name deploy",
        is_app=False,
    )

    _run_asserts()


def test_create_app_without_env_var_with_app_flag(create_folders):
    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "esmerald createproject myproject --deployment-folder-name deploy",
        is_app=False,
    )
    assert ss == 0

    os.chdir("myproject")

    (o, e, ss) = run_cmd(
        "tests.cli.main:app",
        "esmerald --app tests.cli.main:app createdeployment myproject --deployment-folder-name deploy",
        is_app=False,
    )

    _run_asserts()
