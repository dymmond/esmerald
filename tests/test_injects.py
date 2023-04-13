from typing import Any, Dict, Optional

import pytest
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from esmerald.applications import Esmerald
from esmerald.exceptions import ImproperlyConfigured
from esmerald.injector import Inject
from esmerald.params import Injects
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.routing.router import Include
from esmerald.routing.views import APIView
from esmerald.testclient import create_client
from esmerald.utils.constants import IS_DEPENDENCY


def test_is_dependency_inserted_into_field_extra() -> None:
    assert Injects().extra[IS_DEPENDENCY] is True


@pytest.mark.parametrize(
    "field_info, exp",
    [
        (Injects(), None),
        (Injects(default=None), None),
        (Injects(default=13), 13),
    ],
)
def test_dependency_defaults(field_info: Any, exp: Optional[int]) -> None:
    @get("/")
    def handler(value: Optional[int] = field_info) -> Dict[str, Optional[int]]:
        return {"value": value}

    with create_client(routes=[Gateway(handler=handler)]) as client:
        resp = client.get("/")
        assert resp.json() == {"value": exp}


def test_non_optional_with_default() -> None:
    @get("/")
    def handler(value: int = Injects(default=13)) -> Dict[str, int]:
        return {"value": value}

    with create_client(routes=[Gateway(handler=handler)]) as client:
        resp = client.get("/")
        assert resp.json() == {"value": 13}


def test_non_optional_with_default_include() -> None:
    @get("/")
    def handler(value: int = Injects(default=13)) -> Dict[str, int]:
        return {"value": value}

    with create_client(routes=[Include(routes=[Gateway(handler=handler)])]) as client:
        resp = client.get("/")
        assert resp.json() == {"value": 13}


def test_non_optional_with_default_nested_include() -> None:
    @get("/")
    def handler(value: int = Injects(default=13)) -> Dict[str, int]:
        return {"value": value}

    with create_client(
        routes=[Include(routes=[Include(routes=[Gateway(handler=handler)])])]
    ) as client:
        resp = client.get("/")
        assert resp.json() == {"value": 13}


def test_non_optional_with_default_very_nested_include() -> None:
    @get("/")
    def handler(value: int = Injects(default=13)) -> Dict[str, int]:
        return {"value": value}

    with create_client(
        routes=[
            Include(
                routes=[
                    Include(
                        routes=[
                            Include(
                                routes=[
                                    Include(
                                        routes=[
                                            Include(
                                                routes=[
                                                    Include(
                                                        routes=[
                                                            Include(
                                                                routes=[
                                                                    Include(
                                                                        routes=[
                                                                            Gateway(
                                                                                handler=handler
                                                                            )
                                                                        ]
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    ) as client:
        resp = client.get("/")
        assert resp.json() == {"value": 13}


def test_no_default_dependency_Injected() -> None:
    @get(dependencies={"value": Inject(lambda: 13)})
    def test(value: int = Injects()) -> Dict[str, int]:
        return {"value": value}

    with create_client(routes=[Gateway(handler=test)]) as client:
        resp = client.get("/")
    assert resp.json() == {"value": 13}


def test_dependency_not_Injected_and_no_default() -> None:
    @get()
    def test(value: int = Injects()) -> Dict[str, int]:
        return {"value": value}

    with pytest.raises(ImproperlyConfigured):
        Esmerald(routes=[Gateway(handler=test)])


def test_dependency_Injected_on_APIView() -> None:
    class C(APIView):
        path = ""
        dependencies = {"value": Inject(lambda: 13)}

        @get()
        def test(self, value: int = Injects()) -> Dict[str, int]:
            return {"value": value}

    with create_client(routes=[Gateway(handler=C)]) as client:
        resp = client.get("/")
    assert resp.json() == {"value": 13}


def test_dependency_skip_validation() -> None:
    @get("/validated")
    def validated(value: int = Injects()) -> Dict[str, int]:
        return {"value": value}

    @get("/skipped")
    def skipped(value: int = Injects(skip_validation=True)) -> Dict[str, int]:
        return {"value": value}

    with create_client(
        routes=[
            Gateway(handler=validated),
            Gateway(handler=skipped),
        ],
        dependencies={"value": Inject(lambda: "str")},
    ) as client:
        validated_resp = client.get("/validated")
        assert validated_resp.status_code == HTTP_500_INTERNAL_SERVER_ERROR
        skipped_resp = client.get("/skipped")
        assert skipped_resp.status_code == HTTP_200_OK
        assert skipped_resp.json() == {"value": "str"}
