"""
   Initial application creation file
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

# Create a SQL database
db = SQLAlchemy()


def create_app():
    """
    Application factory to create the dogdict app, this is __init__.py file is run first when ever
    flask run command is used in CLI. The application must be started with flask run command!
    """
    app = Flask(__name__, instance_relative_config=True)

    # some common testing config
    app.config.from_mapping(
        SECRET_KEY="test",
        SQLALCHEMY_DATABASE_URI="sqlite:///test.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # swagger configurations
    app.config["SWAGGER"] = {
        "title": "Dogdict API",
        "openapi": "3.0.3",
        "uiversion": 3,
        "doc_dir": "/doc",
    }
    swagger = Swagger(app, template_file="./doc/dogdict.yml")

    # create an entry point to the API
    @app.route("/api/")
    def api_entry_point():
        return "Welcome to the entry point to DogDict API!"

    # Register the SQL database with dogdict app
    with app.app_context():
        db.init_app(app)

    # Import resources and models after defining DB and app to counter circular imports
    from . import api
    from .utils import BreedConverter, FactConverter, GroupConverter, init_db

    # Add db init command to flask cli, test db can be created with command "flask init-db"
    # this replaces populate.py, see details in models.py
    app.cli.add_command(init_db)

    app.url_map.converters["group"] = GroupConverter
    app.url_map.converters["breed"] = BreedConverter
    app.url_map.converters["fact"] = FactConverter
    # register blueprint for API routes
    app.register_blueprint(api.api_bp)

    return app
