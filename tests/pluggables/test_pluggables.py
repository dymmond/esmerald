from esmerald import Esmerald, Pluggable
from esmerald.exceptions import ImproperlyConfigured
from esmerald.testclient import create_client


class MyNewPluggable:
    ...


class CustomPlugglable(Pluggable):
    def plug(self, app: "Esmerald") -> None:
        return super().plug(app)


def test_raises_improperly_configured_for_subsclass(test_client_factory):
    ...

    # pluggables = {"custom": Cus}
