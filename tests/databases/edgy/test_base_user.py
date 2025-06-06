import random
import string
from uuid import uuid4

import edgy
import pytest

from esmerald.conf import settings
from esmerald.contrib.auth.edgy.base_user import AbstractUser

models = edgy.Registry(settings.edgy_database)
pytestmark = pytest.mark.anyio


def get_random_string(length=10):
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
    try:
        await models.create_all()
        yield
        if not models.database.drop:
            await models.drop_all()
    except Exception:
        pytest.skip("No database available")


@pytest.fixture(autouse=True)
async def rollback_transactions():
    with models.database.force_rollback():
        async with models:
            yield


async def test_create_user():
    user = await User.query.create_user(
        first_name="Test",
        last_name="a test",
        email="esmerald@test.com",
        username="user",
        password=get_random_string(),
    )
    users = await User.query.all()

    assert len(users) == 1
    assert users[0].pk == user.pk


async def test_create_superuser():
    uuid = str(uuid4())[:6]
    for _i in range(5):
        await User.query.create_superuser(
            first_name=get_random_string(10),
            last_name=get_random_string(12),
            username=f"{uuid}{get_random_string(10)}",
            email=f"mail@{get_random_string(12)}.com",
            password=get_random_string(8),
        )
    superusers = await User.query.filter(is_superuser=True)
    assert len(superusers) == 5


@pytest.mark.parametrize(
    "password,repeat_password,is_value",
    [("123password", "123password", True), ("123password", "123passwor", False)],
    ids=["check-password-true", "check-password-false"],
)
async def test_check_password(password, repeat_password, is_value):
    uuid = str(uuid4())[:6]
    user = await User.query.create_superuser(
        first_name=get_random_string(10),
        last_name=get_random_string(12),
        username=f"{uuid}{get_random_string(10)}",
        email=f"mail@{get_random_string(12)}.com",
        password=password,
    )

    assert await user.check_password(repeat_password) is is_value


@pytest.mark.parametrize(
    "password,new_password",
    [("123password", "pass223edsd!@3214"), ("-0987ewur3iwohrnf", "3029847389-4u@")],
)
async def test_set_password(password, new_password):
    uuid = str(uuid4())[:6]
    user = await User.query.create_superuser(
        first_name=get_random_string(10),
        last_name=get_random_string(12),
        username=f"{uuid}{get_random_string(10)}",
        email=f"mail@{get_random_string(12)}.com",
        password=password,
    )

    assert await user.check_password(password) is True

    await user.set_password(new_password)

    assert await user.check_password(new_password) is True
    assert await user.check_password(password) is False


async def test_create_normal_users():
    for _i in range(10):
        uuid = str(uuid4())[:6]
        await User.query.create_user(
            first_name=get_random_string(10),
            last_name=get_random_string(12),
            username=f"{uuid}{get_random_string(10)}",
            email=f"mail@{get_random_string(12)}.com",
            password=get_random_string(5),
        )

    users = await User.query.all()

    assert len(users) == 10


async def test_create_normal_all():
    for _i in range(5):
        uuid = str(uuid4())[:6]
        await User.query.create_superuser(
            first_name=get_random_string(10),
            last_name=get_random_string(12),
            username=f"{uuid}{get_random_string(10)}",
            email=f"mail@{get_random_string(12)}.com",
            password=get_random_string(23),
        )

    for _i in range(10):
        uuid = str(uuid4())[:6]
        await User.query.create_user(
            first_name=get_random_string(10),
            last_name=get_random_string(12),
            username=f"{uuid}{get_random_string(10)}",
            email=f"mail@{get_random_string(12)}.com",
            password=get_random_string(12),
        )

    all = await User.query.all()

    assert len(all) == 15

    superusers = await User.query.filter(is_superuser=True)

    assert len(superusers) == 5

    users = await User.query.filter(is_superuser=False)

    assert len(users) == 10
