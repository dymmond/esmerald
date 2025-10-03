import argparse
import random
import string
from typing import Any, Type

from asyncpg.exceptions import UniqueViolationError

from ravyn.core.directives import BaseDirective
from ravyn.core.terminal import Print

from ..main import User

printer = Print()


class Directive(BaseDirective):
    help: str = "Creates a superuser"

    def add_arguments(self, parser: Type["argparse.ArgumentParser"]) -> Any:
        parser.add_argument("--first-name", dest="first_name", type=str, required=True)
        parser.add_argument("--last-name", dest="last_name", type=str, required=True)
        parser.add_argument("--username", dest="username", type=str, required=True)
        parser.add_argument("--email", dest="email", type=str, required=True)
        parser.add_argument("--password", dest="password", type=str, required=True)

    def get_random_string(self, length=10):
        letters = string.ascii_lowercase
        result_str = "".join(random.choice(letters) for i in range(length))
        return result_str

    async def handle(self, *args: Any, **options: Any) -> Any:
        """
        Generates a superuser
        """
        first_name = options["first_name"]
        last_name = options["last_name"]
        username = options["username"]
        email = options["email"]
        password = options["password"]

        try:
            user = await User.query.create_superuser(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
        except UniqueViolationError:
            printer.write_error(f"User with email {email} already exists.")
            return

        printer.write_success(f"Superuser {user.email} created successfully.")
