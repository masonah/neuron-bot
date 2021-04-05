from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    """Construct core application"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)
    # app.run(debug=True)

    with app.app_context():
        from . import routes
        # db.create all # create sql tables for data models

        return app
