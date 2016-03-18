import flask
from flask.ext import sqlalchemy
from flask.ext import whooshalchemy
import functools
import os
import sys

from ufo.services.custom_exceptions import SetupNeeded

app = flask.Flask(__name__, instance_relative_config=True)

app.config.from_object('config.BaseConfiguration')

# Register logging.  Ensure INFO level is captured by Heroku's Logplex.
import logging
stream_handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)

if 'DATABASE_URL' in os.environ:
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
  app.config['WHOOSH_BASE'] = os.environ['DATABASE_URL']

# any instance-specific config the user wants to set, these override everything
app.config.from_pyfile('application.cfg', silent=True)

db = sqlalchemy.SQLAlchemy(app)

# Register the error handlers with the app.
from ufo.services import error_handler
error_handler.init_error_handlers(app)

# DB needs to be defined before this point
from ufo.database import models

whooshalchemy.whoosh_index(app, models.User)
whooshalchemy.whoosh_index(app, models.ProxyServer)

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

from ufo.services import key_distributor
from ufo.handlers import routes
from ufo.services import xsrf
