import pytest

from esmerald.applications import Esmerald
from esmerald.exceptions import ImproperlyConfigured
from esmerald.injector import Inject
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.routing.router import Include


def first_method(query_param: int) -> int:  # pragma: no cover
    assert isinstance(query_param, int)
    return query_param


def second_method(path_param: str) -> str:  # pragma: no cover
    assert isinstance(path_param, str)
    return path_param


def test_dependency_validation() -> None:
    dependencies = {"first": first_method, "second": second_method}

    @get(
        path="/{path_param:int}",
        dependencies=dependencies,
    )
    def test_function(first: int, second: str, third: int) -> None:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Esmerald(
            routes=[Gateway(path="/", handler=test_function)],
            dependencies={
                "third": first_method,
            },
        )


def test_dependency_validation_with_include() -> None:
    dependencies = {"first": first_method, "second": second_method}

    @get(
        path="/{path_param:int}",
        dependencies=dependencies,
    )
    def test_function(first: int, second: str, third: int) -> None:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Esmerald(
            routes=[Include(path="/", routes=[Gateway(path="/", handler=test_function)])],
            dependencies={
                "third": Inject(first_method),
            },
        )


def test_dependency_validation_with_nested_include_mixed() -> None:
    dependencies = {"first": Inject(first_method), "second": second_method}

    @get(
        path="/{path_param:int}",
        dependencies=dependencies,
    )
    def test_function(first: int, second: str, third: int) -> None:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Esmerald(
            routes=[
                Include(
                    path="/",
                    routes=[Include(path="/", routes=[Gateway(path="/", handler=test_function)])],
                )
            ],
            dependencies={
                "third": first_method,
            },
        )


def test_dependency_validation_with_two_nested_include() -> None:
    dependencies = {"first": first_method, "second": second_method}

    @get(
        path="/{path_param:int}",
        dependencies=dependencies,
    )
    def test_function(first: int, second: str, third: int) -> None:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Esmerald(
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
                "third": first_method,
            },
        )


def test_dependency_validation_with_three_nested_include() -> None:
    dependencies = {"first": first_method, "second": second_method}

    @get(
        path="/{path_param:int}",
        dependencies=dependencies,
    )
    def test_function(first: int, second: str, third: int) -> None:
        """ """

    with pytest.raises(ImproperlyConfigured):
        Esmerald(
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
                "third": first_method,
            },
        )
