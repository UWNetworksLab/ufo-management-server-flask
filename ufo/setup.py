from . import app, get_user_config

import flask
import httplib2
import oauth
import oauth2client

from googleapiclient import discovery

@app.route('/not_setup/')
def not_setup():
  return flask.render_template('error.html',
                               error_text='Please finish configuring this site')


@app.route('/setup/', methods=['GET', 'POST'])
def setup():
  """Handle showing the user the setup page and processing the response"""
  config = get_user_config()
  flow = oauth.getOauthFlow()
  oauth_url = flow.step1_get_authorize_url()

  if flask.request.method == 'GET':
    return flask.render_template('setup.html',
                                 config=config,
                                 oauth_url=oauth_url)

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
                                     error='Credentials for another domain',
                                     config=config,
                                     oauth_url=oauth_url)

      userResult = adminApi.users().get(userKey=userId).execute()
      if not userResult.get('isAdmin', False):
        return flask.render_template('setup.html',
                                     error='Credentials do not have admin access',
                                     config=config,
                                     oauth_url=oauth_url)
    except Exception as e:
      logging.error(e, exc_info=True)
      return flask.render_template('setup.html',
                                   error=str(e),
                                   config=config,
                                   oauth_url=oauth_url)

    config.credentials = credentials.to_json()
    config.domain = domain

  config.isConfigured = True

  return flask.redirect(flask.url_for('setup'))
