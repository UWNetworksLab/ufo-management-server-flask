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
PUBLIC_KEY_PATTERN = r'ssh-rsa AAAA[0-9A-Za-z+/]+[=]{0,3} ([^@]+@[^@]+)'
PUBLIC_KEY_ERROR = ('Please supply a valid public key in a format such as '
                    '"ssh-rsa AAAA..."')
app.jinja_env.globals['PUBLIC_KEY_PATTERN'] = PUBLIC_KEY_PATTERN
app.jinja_env.globals['PUBLIC_KEY_ERROR'] = PUBLIC_KEY_ERROR
PRIVATE_KEY_PATTERN = (r'-----BEGIN RSA PRIVATE KEY-----\s[0-9A-Za-z+\/]+'
                       r'[=]{0,3}\s-----END RSA PRIVATE KEY-----')
PRIVATE_KEY_ERROR = ('Please supply a valid private key in a format such as '
                     '"-----BEGIN RSA PRIVATE KEY----- ... '
                     '-----END RSA PRIVATE KEY-----"')
app.jinja_env.globals['PRIVATE_KEY_PATTERN'] = PRIVATE_KEY_PATTERN
app.jinja_env.globals['PRIVATE_KEY_ERROR'] = PRIVATE_KEY_ERROR
# For information on where this huge regex came from, see here:
# http://stackoverflow.com/a/17871737/2216222
IP_V6_REGEX = (r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|'
               r'([0-9a-fA-F]{1,4}:){1,7}:|'
               r'([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|'
               r'([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|'
               r'([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|'
               r'([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|'
               r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|'
               r'[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|'
               r':((:[0-9a-fA-F]{1,4}){1,7}|:)|'
               r'fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|'
               r'::(ffff(:0{1,4}){0,1}:){0,1}'
               r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}'
               r'(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|'
               r'([0-9a-fA-F]{1,4}:){1,4}:'
               r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}'
               r'(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
               r')')
IP_V4_REGEX = (r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|'
               r'(2[0-4]|1{0,1}[0-9]){0,1}[0-9])')
IP_ADDRESS_KEY_PATTERN = IP_V6_REGEX + r'|' + IP_V4_REGEX
IP_ADDRESS_KEY_ERROR = ('Please supply a valid ip address in v4 or v6 format.')
app.jinja_env.globals['IP_ADDRESS_KEY_PATTERN'] = IP_ADDRESS_KEY_PATTERN
app.jinja_env.globals['IP_ADDRESS_KEY_ERROR'] = IP_ADDRESS_KEY_ERROR


db = sqlalchemy.SQLAlchemy(app)

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
import key_distributor
