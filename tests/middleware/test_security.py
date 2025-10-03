from lilya.middleware import DefineMiddleware
from lilya.middleware.security import parse_content_policy

from ravyn import Gateway, Ravyn, get
from ravyn.middleware.security import SecurityMiddleware
from ravyn.responses import PlainText

content_policy_dict = {
    "default-src": "'self'",
    "img-src": [
        "*",
        "data:",
    ],
    "connect-src": "'self'",
    "script-src": "'self'",
    "style-src": ["'self'", "'unsafe-inline'"],
    "script-src-elem": [
        "https://unpkg.com/@stoplight/elements/web-components.min.jss",
    ],
    "style-src-elem": [
        "https://unpkg.com/@stoplight/elements/styles.min.css",
    ],
}


def test_security_policy(test_client_factory):
    @get()
    def homepage() -> PlainText:
        return PlainText("Ok", status_code=200)

    app = Ravyn(
        routes=[Gateway("/", handler=homepage)],
        middleware=[DefineMiddleware(SecurityMiddleware, content_policy=content_policy_dict)],
    )

    client = test_client_factory(app)

    response = client.get("/")

    assert response.headers["content-security-policy"] == parse_content_policy(content_policy_dict)
    assert response.headers["cross-origin-opener-policy"] == "same-origin"
    assert response.headers["referrer-policy"] == "same-origin"
    assert response.headers["strict-transport-security"] == "max-age=31556926; includeSubDomains"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-xss-protection"] == "1; mode=block"
