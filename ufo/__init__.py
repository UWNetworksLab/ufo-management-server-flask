import flask
from flask.ext import sqlalchemy
import functools
import os

app = flask.Flask(__name__, instance_relative_config=True)

# default config values
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'NOT VERY SECRET'

SHARED_OAUTH_CLIENT_ID = '84596478403-6uffc6hu8v5b6v3nh0ski5cbptl02dsd.apps.googleusercontent.com'
SHARED_OAUTH_CLIENT_SECRET = 'R5H27t1C-9enMO9ZNfxym3Gw'

app.config.from_object(__name__)

if 'DATABASE_URL' in os.environ:
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

# any instance-specific config the user wants to set, these override everything
app.config.from_pyfile('application.cfg', silent=True)

db = sqlalchemy.SQLAlchemy(app)

# Set jinja environment globals
app.jinja_env.globals['EMAIL_VALIDATION_PATTERN'] = r'[^@]+@[^@]+.[^@]+'
EMAIL_VALIDATION_ERROR = 'Please supply a valid email address.'
app.jinja_env.globals['EMAIL_VALIDATION_ERROR'] = EMAIL_VALIDATION_ERROR
# Key lookup for users and group allows email or unique id.
KEY_LOOKUP_PATTERN = r'([^@]+@[^@]+.[^@]+|[a-zA-Z0-9]+)'
KEY_LOOKUP_ERROR = 'Please supply a valid email address or unique id.'
app.jinja_env.globals['KEY_LOOKUP_VALIDATION_PATTERN'] = KEY_LOOKUP_PATTERN
app.jinja_env.globals['KEY_LOOKUP_VALIDATION_ERROR'] = KEY_LOOKUP_ERROR

# DB needs to be defined before this point
import database
from models import Config

def get_user_config():
  """Returns the current user-defined configuration from the database"""
  config = database.GetFirstRecord(Config)
  if config is None:
    config = Config()
    config.id = 0
    database.Add(config)

  return config

def setup_required(f):
  """Decorator to handle routes that need setup to have been completed

  This decorator should be applied to nearly all routes"""
  @functools.wraps(f)
  def decorated_function(*args, **kwargs):
    config = get_user_config()
    if not config.isConfigured:
      return flask.redirect(flask.url_for('not_setup'))
    return f(*args, **kwargs)
  return decorated_function

import xsrf
import routes

@app.teardown_appcontext
def shutdown_session(exception=None):
    database.db_session.remove()
