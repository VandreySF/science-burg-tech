"""
Science Burger Tech - Backend application factory.
"""
from flask import Flask


def create_app(config_object: str = "app.config.Config") -> Flask:
    """Application factory."""
    app = Flask(__name__)
    # app.config.from_object(config_object)

    # Register blueprints here as they are created
    # from app.routes.example import example_bp
    # app.register_blueprint(example_bp)

    return app
