from . import app, get_user_config

import datetime
import flask

from oauth2client import client
from oauth2client import util

OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group.readonly',
    'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
    'https://www.googleapis.com/auth/userinfo.email'
]

def getOauthFlow():
  config = get_user_config()
  # TODO give user an option to input their own and go through a different flow
  # to handle it
  return client.OAuth2WebServerFlow(
      client_id=app.config.get('SHARED_OAUTH_CLIENT_ID'),
      client_secret=app.config.get('SHARED_OAUTH_CLIENT_SECRET'),
      scope=util.scopes_to_string(OAUTH_SCOPES),
      redirect_uri='urn:ietf:wg:oauth:2.0:oob',
  )

def getSavedCredentials():
  credentials = getattr(flask.g, '_credentials', None)
  if not credentials:
    config = get_user_config()
    if not config.credentials:
      return None

    credentials = client.OAuth2Credentials.from_json(config.credentials)

    flask.g._credentials = credentials

  return credentials
