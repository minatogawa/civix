import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from logger import get_logger

load_dotenv()

logger = get_logger(__name__)
db = SQLAlchemy()
migrate = Migrate()


def create_app(config=None):
    logger.info("Initializing Flask application")
    app = Flask(__name__)

    # Default configuration
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://civix_user:civix_password@localhost:5432/civix_db"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    logger.info(
        "Flask configuration loaded",
        database_url=database_url.replace(
            database_url.split("@")[0].split("//")[1], "***"
        )
        if "@" in database_url
        else database_url,
        secret_key_set=bool(os.getenv("SECRET_KEY")),
    )

    # Override with test config if provided
    if config:
        logger.info("Applying test configuration overrides")
        app.config.update(config)

    # Initialize extensions
    logger.info("Initializing Flask extensions")
    db.init_app(app)
    migrate.init_app(app, db)

    # Register routes
    from main import register_routes

    logger.info("Registering application routes")
    register_routes(app)

    logger.info("Flask application initialized successfully")
    return app
