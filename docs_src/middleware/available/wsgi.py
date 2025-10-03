from flask import Flask, make_response

from ravyn import Ravyn, Include
from ravyn.middleware.wsgi import WSGIMiddleware

flask = Flask(__name__)


@flask.route("/home")
def home():
    return make_response({"message": "Serving via flask"})


# Add the flask app into Ravyn to be served by Ravyn.
routes = [Include("/external", app=WSGIMiddleware(flask))]

app = Ravyn(routes=routes)
