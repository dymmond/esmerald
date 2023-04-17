import saffier
from saffier import Database, Registry

from esmerald import Esmerald
from esmerald.contrib.auth.saffier.base_user import AbstractUser

database = Database("sqlite:///db.sqlite")
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
