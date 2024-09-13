from esmerald import Gateway, JSONResponse, get
from esmerald.testclient import create_client


@get("/bool")
async def check_bool(a_value: bool) -> JSONResponse:
    return JSONResponse({"value": a_value})


def test_query_param(test_client_factory):
    with create_client(routes=Gateway(handler=check_bool)) as client:

        response = client.get("/bool?a_value=true")

        assert response.status_code == 200
        assert response.json() == {"value": True}

        response = client.get("/bool?a_value=1")
        assert response.json() == {"value": True}

        response = client.get("/bool?a_value=0")
        assert response.json() == {"value": False}

        response = client.get("/bool?a_value=false")
        assert response.json() == {"value": False}
