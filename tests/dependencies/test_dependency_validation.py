import pytest

from ravyn.applications import Ravyn
from ravyn.exceptions import ImproperlyConfigured
from ravyn.injector import Inject
from ravyn.routing.gateways import Gateway
from ravyn.routing.handlers import get
from ravyn.routing.router import Include


def first_method(query_param: int) -> int:  # pragma: no cover
    assert isinstance(query_param, int)
    return query_param


def second_method(path_param: str) -> str:  # pragma: no cover
    assert isinstance(path_param, str)
    return path_param


def test_dependency_validation() -> None:
    dependencies = {"first": Inject(first_method), "second": Inject(second_method)}

    @get(
        path="/{path_param:int}",
        dependencies=dependencies,
    )
    def test_function(first: int, second: str, third: int) -> None:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Ravyn(
            routes=[Gateway(path="/", handler=test_function)],
            dependencies={
                "third": Inject(first_method),
            },
        )


def test_dependency_validation_with_include() -> None:
    dependencies = {"first": Inject(first_method), "second": Inject(second_method)}

    @get(
        path="/{path_param:int}",
        dependencies=dependencies,
    )
    def test_function(first: int, second: str, third: int) -> None:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Ravyn(
            routes=[Include(path="/", routes=[Gateway(path="/", handler=test_function)])],
            dependencies={
                "third": Inject(first_method),
            },
        )


def test_dependency_validation_with_nested_include() -> None:
    dependencies = {"first": Inject(first_method), "second": Inject(second_method)}

    @get(
        path="/{path_param:int}",
        dependencies=dependencies,
    )
    def test_function(first: int, second: str, third: int) -> None:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Ravyn(
            routes=[
                Include(
                    path="/",
                    routes=[Include(path="/", routes=[Gateway(path="/", handler=test_function)])],
                )
            ],
            dependencies={
                "third": Inject(first_method),
            },
        )


def test_dependency_validation_with_two_nested_include() -> None:
    dependencies = {"first": Inject(first_method), "second": Inject(second_method)}

    @get(
        path="/{path_param:int}",
        dependencies=dependencies,
    )
    def test_function(first: int, second: str, third: int) -> None:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Ravyn(
            routes=[
                Include(
                    path="/",
                    routes=[
                        Include(
                            path="/",
                            routes=[
                                Include(
                                    path="/",
                                    routes=[Gateway(path="/", handler=test_function)],
                                )
                            ],
                        )
                    ],
                )
            ],
            dependencies={
                "third": Inject(first_method),
            },
        )


def test_dependency_validation_with_three_nested_include() -> None:
    dependencies = {"first": Inject(first_method), "second": Inject(second_method)}

    @get(
        path="/{path_param:int}",
        dependencies=dependencies,
    )
    def test_function(first: int, second: str, third: int) -> None:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Ravyn(
            routes=[
                Include(
                    path="/",
                    routes=[
                        Include(
                            path="/",
                            routes=[
                                Include(
                                    path="/",
                                    routes=[
                                        Include(
                                            path="/",
                                            routes=[Gateway(path="/", handler=test_function)],
                                        )
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ],
            dependencies={
                "third": Inject(first_method),
            },
        )
