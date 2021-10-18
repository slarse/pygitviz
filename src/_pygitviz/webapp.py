import pathlib

import flask
from flask_cors import CORS

from _pygitviz import util

def create_app(git_root: pathlib.Path, dot_file: pathlib.Path) -> flask.Flask:
    app = flask.Flask(__name__)
    CORS(app)

    @app.route("/graphviz")
    def get_graphviz():
        return dot_file.read_text(encoding=util.ENCODING)

    return app

