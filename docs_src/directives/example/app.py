import edgy
from edgy import Database, Registry

from esmerald import Esmerald
from esmerald.contrib.auth.edgy.base_user import AbstractUser

database = Database("postgres://postgres:password@localhost:5432/my_db")
registry = Registry(database=database)


class User(AbstractUser):
    date_of_birth = edgy.DateField(null=True)

    class Meta:
        registry = registry


def get_application():
    """
    This is optional. The function is only used for organisation purposes.
    """

    app = Esmerald(
        routes=[],
        on_startup=[database.__anter__],
        on_shutdown=[database.__aexit__],
    )

    return app


app = get_application()
