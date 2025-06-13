import random
import string
from typing import Annotated

from sayer import Option, command, success

from esmerald.core.directives.decorator import directive
from tests.cli.simple.test_custom_directive import User


def get_random_string(length=10):
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


@directive
@command
async def create(
    name: Annotated[str, Option(None, "-n", required=True)],
):
    """
    Test directive for creating a user
    """
    user = await User.query.create_superuser(
        first_name=name,
        last_name="lilya",
        username=get_random_string(10),
        email="mail@lilya.dev",
        password=get_random_string(8),
    )
    success(f"Superuser {user.email} created successfully.")
