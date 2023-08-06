import os

class BaseConfig:
    """
    Parent class
    """

    ## flask options ##
    PROJECT = 'tiny contest winners'
    DEBUG = False
    TESTING = False
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.getenv('FLASK_SECRET', 'TerribleLifeChoices')
    WFT_SECRET_KEY = os.getenv('FLASK_SECRET', 'TerribleLifeChoices')
    WTF_CSRF_ENABLED = True
    CSRF_ENABLED = True

    ## database options ##
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/test.db')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ## recaptcha options ##
    RECAPTCHA_USE_SSL = True
    RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', None)
    RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', None)
    RECAPTCHA_OPTIONS = {'theme': 'white'}


class Development(BaseConfig):
    """
    For development environment only
    """

    DEBUG = True
    TESTING = True
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class Production(BaseConfig):
    """
    For production environment only
    """

    # SERVER_NAME = os.getenv('FLASK_SERVER_NAME', 'localhost')
    pass
