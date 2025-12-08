from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)


    db.init_app(app)


    # Models must be imported so SQLAlchemy is aware of them
    from .models import games, teams, news # noqa: F401


    # Register blueprints
    from .routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")


    # Simple health route
    @app.get("/")
    def index():
        return {"status": "ok", "service": "flask-dwh-starter"}


    return app