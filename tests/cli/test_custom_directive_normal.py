import os
import shutil

import pytest

from tests.cli.utils import run_cmd


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


def generate():
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject")
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createapp myapp")


def test_custom_directive(create_folders):
    original_path = os.getcwd()

    generate()

    # Back to starting point
    os.chdir(original_path)

    # Copy the createsuperuser custom directive
    shutil.copyfile(
        "normal_directive.py",
        "myproject/myproject/apps/myapp/directives/operations/normal_directive.py",
    )

    # Execute custom directive
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald run --directive normal_directive")

    assert "Working" in str(o)
