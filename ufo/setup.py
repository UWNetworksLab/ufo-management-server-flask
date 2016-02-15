from . import app, get_user_config

import flask
import httplib2
import oauth
import oauth2client

from googleapiclient import discovery

from ufo import auth
from ufo import models

PLEASE_CONFIGURE_TEXT = 'Please finish configuring this site.'
DOMAIN_INVALID_TEXT = 'Credentials for another domain.'
NON_ADMIN_TEXT = 'Credentials do not have admin access.'
NO_ADMINISTRATOR = 'Please enter an administrator username or password'


class SetupNeeded(Exception):
  code = 500
  message = PLEASE_CONFIGURE_TEXT


@app.route('/setup/', methods=['GET', 'POST'])
@auth.login_required_if_setup
def setup():
  """Handle showing the user the setup page and processing the response"""
  config = get_user_config()
  flow = oauth.getOauthFlow()
  oauth_url = flow.step1_get_authorize_url()

  if flask.request.method == 'GET':
    return flask.render_template('setup.html',
                                 config=config,
                                 oauth_url=oauth_url)

  credentials = None
  domain = flask.request.form.get('domain', None)
  if flask.request.form.get('oauth_code', None):
    try:
      credentials = flow.step2_exchange(flask.request.form['oauth_code'])
    except oauth2client.client.FlowExchangeError as e:
      flask.abort(403) # TODO better error

    apiClient = credentials.authorize(httplib2.Http())
    plusApi = discovery.build(serviceName='plus',
                              version='v1',
                              http=apiClient)
    adminApi = discovery.build(serviceName='admin',
                               version='directory_v1',
                               http = apiClient)

    try:
      profileResult = plusApi.people().get(userId='me').execute()

      if domain is None or domain != profileResult.get('domain', None):
        return flask.render_template('setup.html',
                                     error=DOMAIN_INVALID_TEXT,
                                     config=config,
                                     oauth_url=oauth_url)

      user_id = profileResult['id']
      userResult = adminApi.users().get(userKey=user_id).execute()
      if not userResult.get('isAdmin', False):
        return flask.render_template('setup.html',
                                     error=NON_ADMIN_TEXT,
                                     config=config,
                                     oauth_url=oauth_url)
    except Exception as e:
      logging.error(e, exc_info=True)
      return flask.render_template('setup.html',
                                   error=str(e),
                                   config=config,
                                   oauth_url=oauth_url)

  if not config.isConfigured:
    admin_username = flask.request.form.get('admin_username', None)
    admin_password = flask.request.form.get('admin_password', None)

    if admin_username is None or admin_password is None:
      return flask.render_template('setup.html',
          error=NO_ADMINISTRATOR,
          config=config,
          oauth_url=oauth_url)

    admin_user = models.ManagementServerUser(username=admin_username)
    admin_user.set_password(admin_password)
    admin_user.save()

  # if credentials were set above, moved down here to give us a chance to error
  # out of admin user and password, could be moved inline with proper form
  # validation for that (we also don't want to create a user if another step
  # is going to fail)
  if credentials is not None:
    config.credentials = credentials.to_json()
    config.domain = domain

  config.isConfigured = True
  config.save()

  return flask.redirect(flask.url_for('setup'))
