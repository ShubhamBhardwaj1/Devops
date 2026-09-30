"""Application factory and local development entry point."""

import os
from pathlib import Path

from flask import Flask

from .database import get_db, init_app, init_db
from .routes import bp


def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # VULNERABILITY: hard-coded secret key committed to source control.
        SECRET_KEY="secureguard-development-secret",
        DATABASE=str(Path(app.instance_path) / "secureguard.db"),
        UPLOAD_FOLDER=str(Path(app.instance_path) / "uploads"),
    )

    if test_config:
        app.config.update(test_config)
    else:
        app.config.from_mapping(DATABASE=os.environ.get("DATABASE", app.config["DATABASE"]))

    init_app(app)
    app.register_blueprint(bp)
    with app.app_context():
        init_db()
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
