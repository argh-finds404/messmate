from flask import Flask
from app.config import Config
from app.db import connect, init_schema


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="web/templates")
    app.config.from_object(config_class)

    conn = connect(app.config["DATABASE"])
    init_schema(conn)
    app.extensions["db"] = conn

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}

    return app
