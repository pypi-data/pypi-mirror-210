import os
from flask import Flask, render_template
from tcw.config import Development, Production
from tcw.database import init_db


BASEDIR = os.path.abspath(os.path.dirname(__file__))


def create_app(name='tiny contest winners', config=None, root=None):
    """
    Create the Flask app

    args:
        - name
        - config object
    """

    if config is None:
        config = Development

    if root is None:
        root = BASEDIR

    app = Flask(name, root_path=root)
    configure_app(app, config)
    load_filters(app)
    load_handlers(app)
    load_blueprints(app)
    load_views()

    return app


def configure_app(app, config):
    """
    Configure the flask app

    args:
        - Flask app instance
        - config object
    """

    init_db(config.SQLALCHEMY_DATABASE_URI, config.DEBUG)
    app.config.from_object(config)


def load_blueprints(app):
    """
    Load flask blueprints from web apps

    args:
        - Flask app instance
    """

    from tcw.apps.contest.views import bp as contest

    app.register_blueprint(contest)


def load_views():
    """
    Load views from any of the web apps
    """

    from tcw.apps.contest import views


def load_filters(app):
    """
    Load custom filters into the apps jinja env

    args:
        - Flask app instance
    """

    from tcw.utils import md_to_html
    app.jinja_env.filters['markdown'] = md_to_html


def page_not_found(e=None):
    return render_template('404.html')


def page_expired(e=None):
    return render_template('410.html')


def load_handlers(app):
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(410, page_expired)
