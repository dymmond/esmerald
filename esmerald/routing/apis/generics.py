from typing import ClassVar

from esmerald.routing.apis.views import ListView, SimpleAPIView


class GenericMixin:
    __is_generic__: ClassVar[bool] = True


class CreateAPIView(GenericMixin, SimpleAPIView):
    """
    View that only allows the methods for creation
    of objects.
    """

    http_allowed_methods = ["post", "put", "patch"]


class DeleteAPIView(GenericMixin, SimpleAPIView):
    """
    View that only allows the methods for creation
    of objects.
    """

    http_allowed_methods = ["delete"]


class ReadAPIView(GenericMixin, SimpleAPIView):
    """
    View that only allows the methods for creation
    of objects.
    """

    http_allowed_methods = ["get"]


class ListAPIView(GenericMixin, ListView):
    """
    Only allows the return to be lists.
    """

    ...
