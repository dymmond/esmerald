from flask import Flask, escape, request

from esmerald import ChildEsmerald, Esmerald, Gateway, Include, Request, get
from esmerald.middleware import WSGIMiddleware

flask_app = Flask(__name__)
second_flask_app = Flask(__name__)


@flask_app.route("/")
def flask_main():
    name = request.args.get("name", "Esmerald")
    return f"Hello, {escape(name)} from your Flask integrated!"


@get("/home/{name:str}")
async def home(request: Request) -> dict:
    name = request.path_params["name"]
    return {"name": escape(name)}


@second_flask_app.route("/")
def second_flask_main():
    name = request.args.get("name", "Esmerald")
    return f"Hello, {escape(name)} from Flask!"


child_esmerald = ChildEsmerald(
    routes=[
        Gateway(handler=home),
        Include("/flask", WSGIMiddleware(flask_app)),
        Include("/second/flask", WSGIMiddleware(second_flask_app)),
    ]
)

routes = [Include("/child-esmerald", app=child_esmerald)]

app = Esmerald(routes=routes)
