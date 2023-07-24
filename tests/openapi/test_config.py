from esmerald import Esmerald


def test_swagger_ui_html():
    app = Esmerald(routes=[])

    assert app.settings.openapi_config.swagger_ui_oauth2_redirect_url == "/docs/oauth2-redirect"
