from flask import Flask
from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="web/templates")
    app.config.from_object(config_class)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}

    return app

