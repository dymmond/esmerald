import random
import string

import pytest

from esmerald.conf import settings
from esmerald.contrib.auth.saffier.base_user import AbstractUser

database, models = settings.registry
pytestmark = pytest.mark.anyio


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


class User(AbstractUser):
    """
    Inherits from the abstract user and adds the registry
    from esmerald settings.
    """

    class Meta:
        registry = models


@pytest.fixture(autouse=True, scope="module")
async def create_test_database():
    await models.create_all()
    yield
    await models.drop_all()


@pytest.fixture(autouse=True)
async def rollback_transactions():
    with database.force_rollback():
        async with database:
            yield


async def test_create_user():
    user = await User.create_user(
        first_name="Test",
        last_name="a test",
        email="esmerald@test.com",
        username="user",
        password="123password",
    )
    users = await User.query.all()

    assert len(users) == 1
    assert users[0].pk == user.pk


async def test_create_superuser():
    for i in range(5):
        await User.create_superuser(
            first_name=get_random_string(10),
            last_name=get_random_string(12),
            username=get_random_string(10),
            email=f"mail@{get_random_string(12)}.com",
            password=get_random_string(8),
        )

    superusers = await User.query.filter(is_superuser=True)
    assert len(superusers) == 5


async def test_create_normal_users():
    for i in range(10):
        await User.create_user(
            first_name=get_random_string(10),
            last_name=get_random_string(12),
            username=get_random_string(6),
            email=f"mail@{get_random_string(12)}.com",
            password=get_random_string(5),
        )

    users = await User.query.all()

    assert len(users) == 10


async def test_create_normal_all():
    for i in range(5):
        await User.create_superuser(
            first_name=get_random_string(10),
            last_name=get_random_string(12),
            username=get_random_string(4),
            email=f"mail@{get_random_string(12)}.com",
            password=get_random_string(23),
        )

    for i in range(10):
        await User.create_user(
            first_name=get_random_string(10),
            last_name=get_random_string(12),
            username=get_random_string(5),
            email=f"mail@{get_random_string(12)}.com",
            password=get_random_string(12),
        )

    all = await User.query.all()

    assert len(all) == 15

    superusers = await User.query.filter(is_superuser=True)

    assert len(superusers) == 5

    users = await User.query.filter(is_superuser=False)

    assert len(users) == 10
