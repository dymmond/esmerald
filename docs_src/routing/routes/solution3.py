from flask import Flask, escape, request

from esmerald import Esmerald, Include
from esmerald.middleware.wsgi import WSGIMiddleware

flask_app = Flask(__name__)
another_flask_app = Flask(__name__)


@flask_app.route("/")
def flask_main():
    name = request.args.get("name", "Esmerald")
    return f"Hello, {escape(name)} from Flask!"


app = Esmerald(
    routes=[
        Include(
            "/",
            routes=[
                Include(path="/one", namespace="src.urls"),
                Include(path="/two", namespace="accounts.v1.urls", name="accounts"),
                Include("/flask", WSGIMiddleware(flask_app)),
                Include("/flask/v2", WSGIMiddleware(another_flask_app)),
            ],
            name="root",
        ),
        Include(
            "/external",
            routes=[
                Include(WSGIMiddleware(flask_app)),
            ],
        ),
    ]
)
