import os
import shutil

import pytest

from tests.cli.utils import run_cmd

pytestmark = pytest.mark.anyio


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
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createproject myproject")
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn createapp myapp")


async def test_custom_directive(create_folders):
    original_path = os.getcwd()

    generate()

    # Back to starting point
    os.chdir(original_path)

    # Copy the createuser custom directive
    shutil.copyfile(
        "global_g.py",
        "myproject/myproject/apps/myapp/directives/operations/global_g.py",
    )

    # Execute custom directive
    (o, e, ss) = run_cmd("tests.cli.main:app", "ravyn run global_g")

    assert "Context successfully set to Ravyn from global" in str(o)
