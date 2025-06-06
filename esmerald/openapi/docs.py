import json
from typing import Any, Optional

from lilya.responses import HTMLResponse

swagger_ui_default_parameters = {
    "dom_id": "#swagger-ui",
    "layout": "BaseLayout",
    "deepLinking": True,
    "showExtensions": True,
    "showCommonExtensions": True,
}


def get_swagger_ui_html(
    *,
    openapi_url: str,
    title: str,
    swagger_js_url: str,
    swagger_css_url: str,
    swagger_favicon_url: str,
    oauth2_redirect_url: Optional[str] = None,
    init_oauth: Optional[dict[str, Any]] = None,
    swagger_ui_parameters: Optional[dict[str, Any]] = None,
) -> HTMLResponse:  # pragma: no cover
    current_swagger_ui_parameters = swagger_ui_default_parameters.copy()
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """

    for key, value in current_swagger_ui_parameters.items():
        html += f"{json.dumps(key)}: {json.dumps(value)},\n"

    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"

    html += """
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })"""

    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(init_oauth)})
        """

    html += """
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


def get_redoc_html(
    *,
    openapi_url: str,
    title: str,
    redoc_js_url: str,
    redoc_favicon_url: str,
    with_google_fonts: bool = True,
) -> HTMLResponse:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>{title}</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    """
    if with_google_fonts:
        html += """
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    """
    html += f"""
    <link rel="shortcut icon" href="{redoc_favicon_url}">
    <!--
    ReDoc doesn't change outer page styles
    -->
    <style>
      body {{
        margin: 0;
        padding: 0;
      }}
    </style>
    </head>
    <body>
    <noscript>
        ReDoc requires Javascript to function. Please enable it to browse the documentation.
    </noscript>
    <redoc spec-url="{openapi_url}"></redoc>
    <script src="{redoc_js_url}"> </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


def get_stoplight_html(
    openapi_url: str,
    title: str,
    stoplight_css: str,
    stoplight_js: str,
    stoplight_favicon_url: str,
    style: str = "body { margin: 0; padding: 0 }",
) -> HTMLResponse:
    """Renders the new stoplight openapi docs"""
    html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>{title}</title>
            <!-- needed for adaptive design -->
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link rel="shortcut icon" href="{stoplight_favicon_url}">
            <link rel="stylesheet" href="{stoplight_css}">
            <script src="{stoplight_js}" crossorigin></script>
            <style>{style}</style>
    """
    html += f"""
        <body>
            <noscript>
                Stoplight requires Javascript to function. Please enable it to browse the documentation.
            </noscript>
            <elements-api
                apiDescriptionUrl="{openapi_url}"
                router="hash"
                layout="sidebar"
            />
        </body>
    </html>
    """
    return HTMLResponse(html)


def get_swagger_ui_oauth2_redirect_html() -> HTMLResponse:
    # copied from https://github.com/swagger-api/swagger-ui/blob/v4.14.0/dist/oauth2-redirect.html
    html = """
    <!doctype html>
    <html lang="en-US">
    <head>
        <title>Swagger UI: OAuth2 Redirect</title>
    </head>
    <body>
    <script>
        'use strict';
        function run () {
            var oauth2 = window.opener.swaggerUIRedirectOauth2;
            var sentState = oauth2.state;
            var redirectUrl = oauth2.redirectUrl;
            var isValid, qp, arr;

            if (/code|token|error/.test(window.location.hash)) {
                qp = window.location.hash.substring(1).replace('?', '&');
            } else {
                qp = location.search.substring(1);
            }

            arr = qp.split("&");
            arr.forEach(function (v,i,_arr) { _arr[i] = '"' + v.replace('=', '":"') + '"';});
            qp = qp ? JSON.parse('{' + arr.join() + '}',
                    function (key, value) {
                        return key === "" ? value : decodeURIComponent(value);
                    }
            ) : {};

            isValid = qp.state === sentState;

            if ((
              oauth2.auth.schema.get("flow") === "accessCode" ||
              oauth2.auth.schema.get("flow") === "authorizationCode" ||
              oauth2.auth.schema.get("flow") === "authorization_code"
            ) && !oauth2.auth.code) {
                if (!isValid) {
                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "warning",
                        message: "Authorization may be unsafe, passed state was changed in server. The passed state wasn't returned from auth server."
                    });
                }

                if (qp.code) {
                    delete oauth2.state;
                    oauth2.auth.code = qp.code;
                    oauth2.callback({auth: oauth2.auth, redirectUrl: redirectUrl});
                } else {
                    let oauthErrorMsg;
                    if (qp.error) {
                        oauthErrorMsg = "["+qp.error+"]: " +
                            (qp.error_description ? qp.error_description+ ". " : "no accessCode received from the server. ") +
                            (qp.error_uri ? "More info: "+qp.error_uri : "");
                    }

                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "error",
                        message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server."
                    });
                }
            } else {
                oauth2.callback({auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl});
            }
            window.close();
        }

        if (document.readyState !== 'loading') {
            run();
        } else {
            document.addEventListener('DOMContentLoaded', function () {
                run();
            });
        }
    </script>
    </body>
    </html>
        """
    return HTMLResponse(content=html)


def get_rapidoc_ui_html(
    *,
    openapi_url: str,
    title: str,
    rapidoc_js_url: str,
    rapidoc_favicon_url: str,
    style: str = "body { margin: 0; padding: 0 }",
) -> HTMLResponse:  # pragma: no cover
    """Renders the new stoplight openapi docs"""
    print(rapidoc_favicon_url)
    html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>{title}</title>
            <link rel="shortcut icon" href="{rapidoc_favicon_url}">
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="{rapidoc_js_url}" crossorigin></script>
            <style>{style}</style>
    """
    html += f"""
        <body>
            <noscript>
                Rapidoc requires Javascript to function. Please enable it to browse the documentation.
            </noscript>
            <rapi-doc spec-url="{openapi_url}" />
        </body>
    </html>
    """
    return HTMLResponse(html)
