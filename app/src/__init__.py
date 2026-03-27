from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)

    if config:
        app.config.from_object(config)
    else:
        from .config import Config
        app.config.from_object(Config)

    db.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
