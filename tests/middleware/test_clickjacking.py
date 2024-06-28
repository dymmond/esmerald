from lilya.middleware import DefineMiddleware

from esmerald import Esmerald, Gateway, get
from esmerald.middleware.clickjacking import XFrameOptionsMiddleware
from esmerald.responses import PlainText
from esmerald.testclient import override_settings


def test_xframe_options_deny_responses(test_client_factory):

    @get()
    def homepage() -> PlainText:
        return PlainText("Ok", status_code=200)

    app = Esmerald(
        routes=[Gateway("/", handler=homepage)],
        middleware=[DefineMiddleware(XFrameOptionsMiddleware)],
    )

    client = test_client_factory(app)

    response = client.get("/")

    assert response.headers["x-frame-options"] == "DENY"


@override_settings(x_frame_options="SAMEORIGIN")
def test_xframe_options_same_origin_responses(test_client_factory):
    @get()
    def homepage() -> PlainText:
        return PlainText("Ok", status_code=200)

    app = Esmerald(
        routes=[Gateway("/", handler=homepage)],
        middleware=[DefineMiddleware(XFrameOptionsMiddleware)],
    )

    client = test_client_factory(app)

    response = client.get("/")

    assert response.headers["x-frame-options"] == "SAMEORIGIN"


@override_settings(x_frame_options=None)
def test_xframe_options_defaults(test_client_factory):
    @get()
    def homepage() -> PlainText:
        return PlainText("Ok", status_code=200)

    app = Esmerald(
        routes=[Gateway("/", handler=homepage)],
        middleware=[DefineMiddleware(XFrameOptionsMiddleware)],
    )

    client = test_client_factory(app)

    response = client.get("/")

    assert response.headers["x-frame-options"] == "DENY"
