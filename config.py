"""Flask configuration variables."""
from os import environ, path, getenv
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
# override existing variable in the environment
load_dotenv(override=True)
print(f"DIRECTORY: {path.join(basedir, '.env')}")


class Config:
    """Set Flask configuration from .env file."""

    # General Config
    SLACK_CLIENT_SECRET = environ.get('SLACK_CLIENT_SECRET')
    FLASK_APP = getenv('FLASK_APP')
    FLASK_ENV = getenv('FLASK_ENV')
    SLACK_BOT_TOKEN = getenv('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET = getenv('SLACK_SIGNING_SECRET')

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    print(f"TOKEN: {SLACK_BOT_TOKEN}")
