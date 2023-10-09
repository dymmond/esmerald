from esmerald.routing.apis._metaclasses import ListAPIMeta, SimpleAPIMeta
from esmerald.routing.apis._mixins import MethodMixin
from esmerald.routing.apis.base import View


class SimpleAPIView(View, MethodMixin, metaclass=SimpleAPIMeta):
    """The Esmerald SimpleAPIView class.

    Subclassing this class will create a view using Class Based Views.
    """


class ListView(View, MethodMixin, metaclass=ListAPIMeta):
    """
    Base API for views returning lists.
    """

    ...


class APIView(View):
    """The Esmerald APIView class.

    Subclassing this class will create a view using Class Based Views for everyting.
    """

    ...
