import json

import flask
from googleapiclient import discovery
import httplib2
import oauth2client

import ufo
from ufo.database import models
from ufo.handlers import auth
from ufo.handlers import chrome_policy
from ufo.handlers import user
from ufo.handlers import proxy_server
from ufo.handlers import settings
from ufo.services import oauth


# TODO(eholder): Make these errors actually show up in the UI or do
# something else that is useful with them.
DOMAIN_INVALID_TEXT = 'Credentials for another domain.'
NON_ADMIN_TEXT = 'Credentials do not have admin access.'
NO_ADMINISTRATOR = 'Please enter an administrator username or password.'


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
    'hasAddFlow': False,
    'oauth_url': oauth_url,
    'setup_url': flask.url_for('setup'),
    'titleText': 'Oauth Configuration',
    'welcomeText': ('Hey there! Welcome to the uProxy for Organizations '
        'management server! To start, we want to get a bit of information from'
        ' you to get everything set up.'),
    'googleDomainPromptText': ('First of all, if you are planning on using '
        'this application with a Google apps domain, we\'re going to need to '
        'get permission from you to access that. This will be used to keep '
        'the list of users in your domain in sync with who is allowed to '
        'access the uProxy servers. The credentials you authorize will be '
        'shared by any administrators who log into this server. If you do not '
        'plan on using a Google apps domain with this product, you can just go'
        ' straight to adding users.'),
    'successSetupText': ('You have already successfully configured this '
        'deployment! If you want to change the settings, you may do so below. '
        'Please note: submitting the form even without filling in any '
        'parameters will cause the previous saved configuration to be lost.'),
    'domainConfiguredText': ('This site is set up to work with the following '
        'domain. If that is not correct, please update the configuration.'),
    'noDomainConfiguredText': ('This site is not set up to use any Google apps'
        ' domain name. All users will need to be manually input.'),
    'betaWarningText': ('Please keep in mind that this is a much simpler '
        'version than what you would actually expect to see in a finished '
        'version of the site. Noteably, this page should include something '
        'about authenticating yourself in the future (and actually include a '
        'way to skip).'),
    'connectYourDomainButtonText': 'Connect to Your Domain',
    'pasteTheCodeText': ('Once you finish authorizing access, please paste the'
        ' code you receive in the box below.'),
    'submitButtonText': 'Submit',
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
    user_resources_dict = user.get_user_resources_dict()
    user_resources_dict['hasAddFlow'] = False
    proxy_server_resources_dict = proxy_server.get_proxy_resources_dict()
    proxy_server_resources_dict['hasAddFlow'] = False
    policy_resources_dict = chrome_policy.get_policy_resources_dict()
    settings_resources_dict = settings.get_settings_resources_dict()

    return flask.render_template(
        'setup.html',
        oauth_url=oauth_url,
        settings_resources=json.dumps(settings_resources_dict),
        policy_resources=json.dumps(policy_resources_dict),
        proxy_server_resources=json.dumps(proxy_server_resources_dict),
        oauth_resources=json.dumps(oauth_resources_dict),
        user_resources=json.dumps(user_resources_dict))

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
            oauth_resources=json.dumps(oauth_resources_dict))

      user_id = profileResult['id']
      userResult = adminApi.users().get(userKey=user_id).execute()
      if not userResult.get('isAdmin', False):
        return flask.render_template(
            'setup.html', error=NON_ADMIN_TEXT,
            oauth_resources=json.dumps(oauth_resources_dict))
    except Exception as e:
      ufo.app.logger.error(e, exc_info=True)
      return flask.render_template(
          'setup.html', error=str(e),
          oauth_resources=json.dumps(oauth_resources_dict))

  if not config.isConfigured:
    admin_username = flask.request.form.get('admin_username', None)
    admin_password = flask.request.form.get('admin_password', None)

    if admin_username is None or admin_password is None:
      return flask.render_template(
          'setup.html', error=NO_ADMINISTRATOR,
          oauth_resources=json.dumps(oauth_resources_dict))

    admin_user = models.AdminUser(username=admin_username)
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
