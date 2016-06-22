import flask
from flask import request
from flask.ext import sqlalchemy
from flask.ext import whooshalchemy
from flask_recaptcha import ReCaptcha
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

if 'RECAPTCHA_SITE_KEY' in os.environ and 'RECAPTCHA_SECRET_KEY' in os.environ:
  app.config['RECAPTCHA_SITE_KEY'] = os.environ['RECAPTCHA_SITE_KEY']
  app.config['RECAPTCHA_SECRET_KEY'] = os.environ['RECAPTCHA_SECRET_KEY']
else:
  app.logger.error('No recaptcha site or secret key found. Please configure ' +
                   'RECAPTCHA_SITE_KEY and RECAPTCHA_SECRET_KEY in the ' +
                   'environment variables.')

# any instance-specific config the user wants to set, these override everything
app.config.from_pyfile('application.cfg', silent=True)

db = sqlalchemy.SQLAlchemy(app)

# Register the error handlers with the app.
from ufo.services import error_handler
error_handler.init_error_handlers(app)

# DB needs to be defined before this point
from ufo.database import models

try:
  whooshalchemy.whoosh_index(app, models.User)
  whooshalchemy.whoosh_index(app, models.ProxyServer)
except:
  app.logger.error('Whoosh indexing failed. Search may be broken as result. '
                   'Please redeploy to correct this.')

# The headers and prefix listed below are to help guard against XSSI. The
# prefix specifically causes us to escape out of any client that attempts to
# execute the JSON as code. We don't use any callbacks or functions in our
# returned JSON, but the prefix would catch it by causing execution to stop if
# so. The prefix is supplied in the resource dictionaries so that it can be
# stripped away on the client side when making AJAX calls.
JSON_HEADERS = {'Content-Type': 'application/javascript; charset=utf-8'}
XSSI_PREFIX = ")]}'\n"

RECAPTCHA = ReCaptcha(app=app)

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
from ufo.services import resource_provider


@app.before_first_request
def set_jinja_before_request():
  """Set the global jinja environment vars."""
  resource_provider.set_jinja_globals()

DEFAULT_LANGUAGE_PREFIX = 'en'
ACCEPTABLE_LANGUAGE_PREFIXES = [
  'en',
  'es',
  'fr',
  'it',
] # These aren't necessarily true, just something to test with.

@app.before_request
def determine_language_prefix():
  """Determine the language prefix using the language header."""
  # TODO(eholder): Figure out a more appropriate way to map the header into
  # our set of prefixes. Since I don't know what those prefixes are yet, this
  # is intentionally very generic. I also need to decide if this should just be
  # done once as part of the login flow rather than checking every request.
  # Checking every request makes this easier to test and change though in the
  # meantime.
  languages_string = request.headers.get('Accept-Language')

  # If there is no header, use the default.
  if languages_string is None:
    flask.session['language_prefix'] = DEFAULT_LANGUAGE_PREFIX
    return

  languages = languages_string.split(',')
  if languages[0] in ACCEPTABLE_LANGUAGE_PREFIXES:
    flask.session['language_prefix'] = languages[0]
    return

  language_sections = languages[0].split(';')
  if language_sections[0] in ACCEPTABLE_LANGUAGE_PREFIXES:
    flask.session['language_prefix'] = language_sections[0]
    return

  language_subsections = language_sections[0].split('-')
  if language_subsections[0] in ACCEPTABLE_LANGUAGE_PREFIXES:
    flask.session['language_prefix'] = language_subsections[0]
    return

  flask.session['language_prefix'] = DEFAULT_LANGUAGE_PREFIX
