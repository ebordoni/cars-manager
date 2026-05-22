import os
import secrets
from flask import Flask
from database import init_db
from routes import register_routes


class IngressMiddleware:
    """Middleware to handle Home Assistant ingress path prefix."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        ingress_path = environ.get("HTTP_X_INGRESS_PATH", "")
        if ingress_path:
            environ["SCRIPT_NAME"] = ingress_path
        return self.app(environ, start_response)


def create_app():
    app = Flask(__name__)

    # Secret key: use a persistent one stored in /data to survive restarts
    secret_key_file = "/data/.secret_key"
    if os.path.exists(secret_key_file):
        with open(secret_key_file, "r") as f:
            app.config["SECRET_KEY"] = f.read().strip()
    else:
        key = secrets.token_hex(32)
        with open(secret_key_file, "w") as f:
            f.write(key)
        app.config["SECRET_KEY"] = key

    app.config["UPLOAD_FOLDER"] = "/data/uploads/documents"
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB

    # Initialize database and directories
    init_db()

    # Register all blueprints
    register_routes(app)

    # Apply ingress middleware
    app.wsgi_app = IngressMiddleware(app.wsgi_app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
