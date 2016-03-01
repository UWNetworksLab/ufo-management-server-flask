import json

import flask
from googleapiclient import discovery
import httplib2
import oauth2client

import ufo
from ufo.handlers import chrome_policy
from ufo.services import oauth
from ufo.handlers import user


DOMAIN_INVALID_TEXT = 'Credentials for another domain.'
NON_ADMIN_TEXT = 'Credentials do not have admin access.'


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
  }


@ufo.app.route('/setup/', methods=['GET', 'POST'])
def setup():
  """Handle showing the user the setup page and processing the response"""

  config = ufo.get_user_config()
  flow = oauth.getOauthFlow()
  oauth_url = flow.step1_get_authorize_url()

  if flask.request.method == 'GET':
    user_resources_dict = user.get_user_resources_dict()
    user_resources_dict['hasAddFlow'] = False
    oauth_resources_dict = _get_oauth_configration_resources_dict(config,
                                                                  oauth_url)
    policy_resources_dict = chrome_policy.get_policy_resources_dict()

    return flask.render_template(
        'setup.html',
        oauth_url=oauth_url,
        policy_resources=json.dumps(policy_resources_dict),
        oauth_resources=json.dumps(oauth_resources_dict),
        user_resources=json.dumps(user_resources_dict))

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

      if 'domain' in profileResult and profileResult['domain'] and profileResult['domain'] == flask.request.form.get('domain'):
        domain = profileResult['domain']
        userId = profileResult['id']
      else:
        return flask.render_template('setup.html',
                                     error=DOMAIN_INVALID_TEXT,
                                     config=config,
                                     oauth_url=oauth_url)

      userResult = adminApi.users().get(userKey=userId).execute()
      if userResult.get('isAdmin', False):
        config.credentials = credentials.to_json()
        config.domain = domain
      else:
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

  config.isConfigured = True
  config.save()

  return flask.redirect(flask.url_for('setup'))
