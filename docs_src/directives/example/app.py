import saffier
from esmerald import Esmerald
from esmerald.contrib.auth.saffier.base_user import AbstractUser
from saffier import Database, Registry

database = Database("postgres://postgres:password@localhost:5432/my_db")
registry = Registry(database=database)


class User(AbstractUser):
    date_of_birth = saffier.DateField(null=True)

    class Meta:
        registry = registry


def get_application():
    """
    This is optional. The function is only used for organisation purposes.
    """

    app = Esmerald(
        routes=[],
        on_startup=[database.connect],
        on_shutdown=[database.disconnect],
    )

    return app


app = get_application()
