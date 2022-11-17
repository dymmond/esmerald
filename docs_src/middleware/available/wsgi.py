from esmerald import Esmerald, Include
from esmerald.middleware import WSGIMiddleware
from flask import Flask, make_response
from starlette.middleware import Middleware as StarletteMiddleware

flask = Flask(__name__)


@flask.route("/home")
def home():
    return make_response({"message": "Serving via flask"})


# Add the flask app into Esmerald to be served by Esmerald.
routes = [Include("/external", app=WSGIMiddleware(flask))]

app = Esmerald(routes=routes)
