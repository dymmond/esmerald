from flask import Flask, request

from esmerald import Esmerald, Include
from esmerald.middleware import WSGIMiddleware

flask_app = Flask(__name_)
another_flask_app = Flask(__name_)


@flask_app.route("/")
def flask_main():
    name = request.args.get("name", "Esmerald")
    return f"Hello, {name} from Flask!"


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
