from ravyn import Gateway, Ravyn, get
from ravyn.openapi.docs import (
    get_redoc_html,
    get_stoplight_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from ravyn.testclient import EsmeraldTestClient


@get("/")
async def home() -> None:
    """"""


app = Ravyn(routes=[Gateway(handler=home)])
client = EsmeraldTestClient(app)


def test_get_swagger_ui(test_client_factory):
    response = get_swagger_ui_html(
        openapi_url=app.openapi_config.openapi_url,
        title=app.openapi_config.title,
        swagger_js_url=app.openapi_config.swagger_js_url,
        swagger_css_url=app.openapi_config.swagger_css_url,
        swagger_favicon_url=app.openapi_config.swagger_favicon_url,
        oauth2_redirect_url=app.openapi_config.swagger_ui_oauth2_redirect_url,
        init_oauth=app.openapi_config.swagger_ui_init_oauth,
        swagger_ui_parameters=app.openapi_config.swagger_ui_parameters,
    )

    assert response.status_code == 200
    assert (
        response.body
        == b'\n    <!DOCTYPE html>\n    <html>\n    <head>\n    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.4/swagger-ui.min.css">\n    <link rel="shortcut icon" href="https://ravyn.dev/statics/images/favicon.ico">\n    <title>Ravyn</title>\n    </head>\n    <body>\n    <div id="swagger-ui">\n    </div>\n    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.4/swagger-ui-bundle.min.js"></script>\n    <!-- `SwaggerUIBundle` is now available on the page -->\n    <script>\n    const ui = SwaggerUIBundle({\n        url: \'/openapi.json\',\n    "dom_id": "#swagger-ui",\n"layout": "BaseLayout",\n"deepLinking": true,\n"showExtensions": true,\n"showCommonExtensions": true,\noauth2RedirectUrl: window.location.origin + \'/docs/oauth2-redirect\',\n    presets: [\n        SwaggerUIBundle.presets.apis,\n        SwaggerUIBundle.SwaggerUIStandalonePreset\n        ],\n    })\n    </script>\n    </body>\n    </html>\n    '
    )


def test_get_redoc_ui(test_client_factory):
    response = get_redoc_html(
        openapi_url=app.openapi_config.openapi_url,
        title=app.openapi_config.title,
        redoc_js_url=app.openapi_config.redoc_js_url,
        redoc_favicon_url=app.openapi_config.redoc_favicon_url,
        with_google_fonts=app.openapi_config.with_google_fonts,
    )

    assert response.status_code == 200
    assert (
        response.body
        == b'\n    <!DOCTYPE html>\n    <html>\n    <head>\n    <title>Ravyn</title>\n    <!-- needed for adaptive design -->\n    <meta charset="utf-8"/>\n    <meta name="viewport" content="width=device-width, initial-scale=1">\n    \n    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">\n    \n    <link rel="shortcut icon" href="https://ravyn.dev/statics/images/favicon.ico">\n    <!--\n    ReDoc doesn\'t change outer page styles\n    -->\n    <style>\n      body {\n        margin: 0;\n        padding: 0;\n      }\n    </style>\n    </head>\n    <body>\n    <noscript>\n        ReDoc requires Javascript to function. Please enable it to browse the documentation.\n    </noscript>\n    <redoc spec-url="/openapi.json"></redoc>\n    <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>\n    </body>\n    </html>\n    '
    )


def test_get_swagger_ui_oauth2_redirect_html(test_client_factory):
    response = get_swagger_ui_oauth2_redirect_html()

    assert response.status_code == 200
    assert (
        response.body
        == b'\n    <!doctype html>\n    <html lang="en-US">\n    <head>\n        <title>Swagger UI: OAuth2 Redirect</title>\n    </head>\n    <body>\n    <script>\n        \'use strict\';\n        function run () {\n            var oauth2 = window.opener.swaggerUIRedirectOauth2;\n            var sentState = oauth2.state;\n            var redirectUrl = oauth2.redirectUrl;\n            var isValid, qp, arr;\n\n            if (/code|token|error/.test(window.location.hash)) {\n                qp = window.location.hash.substring(1).replace(\'?\', \'&\');\n            } else {\n                qp = location.search.substring(1);\n            }\n\n            arr = qp.split("&");\n            arr.forEach(function (v,i,_arr) { _arr[i] = \'"\' + v.replace(\'=\', \'":"\') + \'"\';});\n            qp = qp ? JSON.parse(\'{\' + arr.join() + \'}\',\n                    function (key, value) {\n                        return key === "" ? value : decodeURIComponent(value);\n                    }\n            ) : {};\n\n            isValid = qp.state === sentState;\n\n            if ((\n              oauth2.auth.schema.get("flow") === "accessCode" ||\n              oauth2.auth.schema.get("flow") === "authorizationCode" ||\n              oauth2.auth.schema.get("flow") === "authorization_code"\n            ) && !oauth2.auth.code) {\n                if (!isValid) {\n                    oauth2.errCb({\n                        authId: oauth2.auth.name,\n                        source: "auth",\n                        level: "warning",\n                        message: "Authorization may be unsafe, passed state was changed in server. The passed state wasn\'t returned from auth server."\n                    });\n                }\n\n                if (qp.code) {\n                    delete oauth2.state;\n                    oauth2.auth.code = qp.code;\n                    oauth2.callback({auth: oauth2.auth, redirectUrl: redirectUrl});\n                } else {\n                    let oauthErrorMsg;\n                    if (qp.error) {\n                        oauthErrorMsg = "["+qp.error+"]: " +\n                            (qp.error_description ? qp.error_description+ ". " : "no accessCode received from the server. ") +\n                            (qp.error_uri ? "More info: "+qp.error_uri : "");\n                    }\n\n                    oauth2.errCb({\n                        authId: oauth2.auth.name,\n                        source: "auth",\n                        level: "error",\n                        message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server."\n                    });\n                }\n            } else {\n                oauth2.callback({auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl});\n            }\n            window.close();\n        }\n\n        if (document.readyState !== \'loading\') {\n            run();\n        } else {\n            document.addEventListener(\'DOMContentLoaded\', function () {\n                run();\n            });\n        }\n    </script>\n    </body>\n    </html>\n        '
    )


def test_get_spotlight_ui(test_client_factory):
    response = get_stoplight_html(
        openapi_url=app.openapi_config.openapi_url,
        title=app.openapi_config.title,
        stoplight_js=app.openapi_config.redoc_js_url,
        stoplight_favicon_url=app.openapi_config.stoplight_favicon_url,
        stoplight_css=app.openapi_config.stoplight_css_url,
    )

    assert response.status_code == 200
    assert (
        response.body
        == b'\n    <!DOCTYPE html>\n    <html>\n        <head>\n            <title>Ravyn</title>\n            <!-- needed for adaptive design -->\n            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">\n            <link rel="shortcut icon" href="https://ravyn.dev/statics/images/favicon.ico">\n            <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">\n            <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js" crossorigin></script>\n            <style>body { margin: 0; padding: 0 }</style>\n    \n        <body>\n            <noscript>\n                Stoplight requires Javascript to function. Please enable it to browse the documentation.\n            </noscript>\n            <elements-api\n                apiDescriptionUrl="/openapi.json"\n                router="hash"\n                layout="sidebar"\n            />\n        </body>\n    </html>\n    '
    )
