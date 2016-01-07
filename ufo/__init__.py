import os
import flask
import functools

from flask.ext import sqlalchemy

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

# DB needs to be defined before this point
import models

@app.after_request
def commitDB(response):
  """Save credentials if changed, then commit the db session"""
  # credentials are cached in the app context, save them if they have changed
  credentials = getattr(flask.g, '_credentials', None)
  if credentials is not None:
    config = get_user_config()
    json_credentials = credentials.to_json()
    if config.credentials != json_credentials:
      config.credentials = json_credentials

  db.session.commit()

  return response

def get_user_config():
  """Returns the current user-defined configuration from the database"""
  config = models.Config.query.get(0)
  if config is None:
    config = models.Config()
    config.id = 0
    db.session.add(config)

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
