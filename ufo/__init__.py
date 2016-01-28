import error_handler
import flask
from flask.ext import sqlalchemy
import functools
import os

app = flask.Flask(__name__, instance_relative_config=True)

app.config.from_object('config.BaseConfiguration')

if 'DATABASE_URL' in os.environ:
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

# any instance-specific config the user wants to set, these override everything
app.config.from_pyfile('application.cfg', silent=True)

# Register the error handlers with the app.
error_handler.init_error_handlers(app)

# TODO(eholder): Move these over to javascript and i18n as appropriate once
# we've decided how to structure the client side code.
# Set jinja environment globals
app.jinja_env.globals['EMAIL_VALIDATION_PATTERN'] = r'[^@]+@[^@]+.[^@]+'
EMAIL_VALIDATION_ERROR = 'Please supply a valid email address.'
app.jinja_env.globals['EMAIL_VALIDATION_ERROR'] = EMAIL_VALIDATION_ERROR
# Key lookup for users and group allows email or unique id.
KEY_LOOKUP_PATTERN = r'([^@]+@[^@]+.[^@]+|[a-zA-Z0-9]+)'
KEY_LOOKUP_ERROR = 'Please supply a valid email address or unique id.'
app.jinja_env.globals['KEY_LOOKUP_VALIDATION_PATTERN'] = KEY_LOOKUP_PATTERN
app.jinja_env.globals['KEY_LOOKUP_VALIDATION_ERROR'] = KEY_LOOKUP_ERROR

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
import models

@app.after_request
def checkCredentialChange(response):
  """Save credentials if changed"""
  credentials = getattr(flask.g, '_credentials', None)
  if credentials is not None:
    config = get_user_config()
    json_credentials = credentials.to_json()
    if config.credentials != json_credentials:
      config.credentials = json_credentials
      config.save()

  return response

def get_user_config():
  """Returns the current user-defined configuration from the database"""
  config = models.Config.query.get(0)
  if config is None:
    config = models.Config()
    config.id = 0

    config.save()

  return config

# only import setup here to avoid circular reference
from setup import SetupNeeded

def setup_required(func):
  """Decorator to handle routes that need setup to have been completed

  This decorator should be applied to nearly all routes"""
  @functools.wraps(func)
  def decorated_function(*args, **kwargs):
    config = get_user_config()
    if not config.isConfigured:
      raise SetupNeeded
    return func(*args, **kwargs)
  return decorated_function

import xsrf
import routes
