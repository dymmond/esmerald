import os
import shutil

import pytest

from esmerald.conf import settings
from esmerald.contrib.auth.saffier.base_user import AbstractUser
from tests.cli.utils import run_cmd

database, models = settings.registry
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


class User(AbstractUser):
    """
    Inherits from the abstract user and adds the registry
    from esmerald settings.
    """

    class Meta:
        registry = models


@pytest.fixture(autouse=True, scope="module")
async def create_test_database():
    try:
        await models.create_all()
        yield
        await models.drop_all()
    except Exception:
        pytest.skip("No database available")


@pytest.fixture(autouse=True)
async def rollback_transactions():
    with database.force_rollback():
        async with database:
            yield


def generate():
    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createproject myproject")
    assert ss == 0

    os.chdir("myproject/myproject/apps")

    (o, e, ss) = run_cmd("tests.cli.main:app", "esmerald createapp myapp")


async def test_custom_directive(create_folders):
    original_path = os.getcwd()

    generate()
    users = await User.query.all()

    assert len(users) == 0

    # Generate the files

    # Back to starting point
    os.chdir(original_path)

    # Copy the createsuperuser custom directive
    shutil.copyfile(
        "createsuperuser.py",
        "myproject/myproject/apps/myapp/directives/operations/createsuperuser.py",
    )

    # Execute custom directive
    name = "Esmerald"
    (o, e, ss) = run_cmd(
        "tests.cli.main:app", f"esmerald run --directive createsuperuser -n {name}"
    )

    users = await User.query.all()

    assert len(users) == 1

    user = await User.query.get(first_name=name)

    assert user.first_name == name
    assert user.email == "mail@esmerald.dev"
    assert user.is_superuser is True
