import argparse
import random
import string
from typing import Any, Type

from esmerald.core.directives import BaseDirective
from esmerald.core.terminal import Print
from tests.cli.test_custom_directive import User

printer = Print()


class Directive(BaseDirective):
    help: str = "Test directive"

    def add_arguments(self, parser: Type["argparse.ArgumentParser"]) -> Any:
        parser.add_argument("-n", "--name", dest="name", type=str, required=True)

    def get_random_string(self, length=10):
        letters = string.ascii_lowercase
        result_str = "".join(random.choice(letters) for i in range(length))
        return result_str

    async def handle(self, *args: Any, **options: Any) -> Any:
        """
        Generates a superuser
        """
        name = options["name"]

        user = await User.query.create_superuser(
            first_name=name,
            last_name="esmerald",
            username=self.get_random_string(10),
            email="mail@esmerald.dev",
            password=self.get_random_string(8),
        )

        printer.write_success(f"Superuser {user.email} created successfully.")
