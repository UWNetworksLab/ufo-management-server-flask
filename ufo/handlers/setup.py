import json

import flask
from googleapiclient import discovery
import httplib2
import oauth2client

import ufo
from ufo.database import models
from ufo.handlers import auth
from ufo.services import oauth


# TODO(eholder): Make these errors actually show up in the UI or do
# something else that is useful with them.
DOMAIN_INVALID_TEXT = 'Credentials for another domain.'
NON_ADMIN_TEXT = 'Credentials do not have admin access.'
NO_ADMINISTRATOR = 'Please enter an administrator email or password.'


def _get_oauth_configration_resources_dict(config, oauth_url):
  """Get the resources for the oauth configuration component.

    Args:
      config: A database object representing the config data.
      oauth_url: A string of the URL to get the oauth code.

    Returns:
      A dict of the resources for the oauth configuration component.
  """
  return {
    'config': config.to_dict(),
    'oauth_url': oauth_url,
  }


@ufo.app.route('/setup/', methods=['GET', 'POST'])
@auth.login_required_if_setup
def setup():
  """Handle showing the user the setup page and processing the response.

  Returns:
    On get: a rendered setup page template with appropriate resources passed
    in. On post: a rendered setup page template with the error set in event of
    a known error, a 403 flask.abort in the event of a FlowExchangeError
    during oauth, or a redirect back to get the setup page on success.
  """

  config = ufo.get_user_config()
  flow = oauth.getOauthFlow()
  oauth_url = flow.step1_get_authorize_url()
  oauth_resources_dict = _get_oauth_configration_resources_dict(config,
                                                                oauth_url)

  if flask.request.method == 'GET':

    return flask.render_template(
        'setup.html',
        oauth_url=oauth_url,
        oauth_configuration_resources=json.dumps(oauth_resources_dict))

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
        return flask.render_template(
            'setup.html', error=DOMAIN_INVALID_TEXT,
            oauth_configuration_resources=json.dumps(oauth_resources_dict))

      user_id = profileResult['id']
      userResult = adminApi.users().get(userKey=user_id).execute()
      if not userResult.get('isAdmin', False):
        return flask.render_template(
            'setup.html', error=NON_ADMIN_TEXT,
            oauth_configuration_resources=json.dumps(oauth_resources_dict))
    except Exception as e:
      ufo.app.logger.error(e, exc_info=True)
      return flask.render_template(
          'setup.html', error=str(e),
          oauth_configuration_resources=json.dumps(oauth_resources_dict))

  if not config.isConfigured:
    admin_email = flask.request.form.get('admin_email', None)
    admin_password = flask.request.form.get('admin_password', None)

    if admin_email is None or admin_password is None:
      return flask.render_template(
          'setup.html', error=NO_ADMINISTRATOR,
          oauth_configuration_resources=json.dumps(oauth_resources_dict))

    admin_user = models.AdminUser(email=admin_email)
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
  config.should_show_recaptcha = False
  config.save()

  return flask.redirect(flask.url_for('setup'))
