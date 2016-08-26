import json

import flask
from googleapiclient import discovery
import httplib2
import oauth2client

import ufo
from ufo.database import models
from ufo.handlers import auth
from ufo.services import oauth



@ufo.app.route('/setup/', methods=['GET'])
@auth.login_required_if_setup
def setup():
  """Handle showing the user the setup page.

  Returns:
    A rendered setup page template with appropriate resources passed in.
  """
  oauth_resources_dict = ufo.make_oauth_configration_resources_dict()

  return flask.render_template(
      'setup.html',
      configuration_resources=json.dumps(oauth_resources_dict))


@ufo.app.route('/setup_admin/', methods=['POST'])
@auth.login_required_if_setup
def setup_admin():
  """Create the first admin in the system from the setup page.

  Returns:
    A json message indicating a redirect to login if successful.
  """
  config = ufo.get_user_config()
  if config.isConfigured:
    flask.abort(403,
                ufo.get_json_message('cantSetAdminAfterInitialSetupError'))

  admin_email = flask.request.form.get('admin_email', None)
  admin_password = flask.request.form.get('admin_password', None)

  if admin_email is None or admin_password is None:
    flask.abort(403, ufo.get_json_message('noAdministratorError'))

  admin_user = models.AdminUser(email=admin_email)
  admin_user.set_password(admin_password)
  admin_user.save()

  config.isConfigured = True
  config.should_show_recaptcha = False
  config.save()

  response_json = json.dumps(({'shouldRedirect': True}))
  return flask.Response(ufo.XSSI_PREFIX + response_json,
                        headers=ufo.JSON_HEADERS)


@ufo.app.route('/setup_oauth/', methods=['POST'])
@auth.login_required
def setup_oauth():
  """Setup oauth for the apps domain.

  Returns:
    A json message indicating success or a flask abort with 403 for oauth
    exceptions.
  """
  oauth_code = flask.request.form.get('oauth_code', None)
  if oauth_code is None:
    flask.abort(403, ufo.get_json_message('noOauthCodeError'))

  config = ufo.get_user_config()
  flow = oauth.getOauthFlow()
  credentials = None
  domain = flask.request.form.get('domain', None)

  try:
    credentials = flow.step2_exchange(oauth_code)
  except oauth2client.client.FlowExchangeError as e:
    flask.abort(403, e.message)

  apiClient = credentials.authorize(httplib2.Http())
  plusApi = discovery.build(serviceName='plus', version='v1', http=apiClient)
  adminApi = discovery.build(serviceName='admin', version='directory_v1',
                             http = apiClient)

  profileResult = None
  try:
    profileResult = plusApi.people().get(userId='me').execute()
  except Exception as e:
    ufo.app.logger.error(e, exc_info=True)
    flask.abort(403, ufo.get_json_message('domainInvalidError'))

  if domain is None or domain != profileResult.get('domain', None):
    flask.abort(403, ufo.get_json_message('domainInvalidError'))

  user_id = profileResult['id']
  userResult = None
  try:
    userResult = adminApi.users().get(userKey=user_id).execute()
  except Exception as e:
    ufo.app.logger.error(e, exc_info=True)
    flask.abort(403, ufo.get_json_message('nonAdminAccessError'))

  if not userResult.get('isAdmin', False):
    flask.abort(403, ufo.get_json_message('nonAdminAccessError'))

  config.credentials = credentials.to_json()
  config.domain = domain
  flask.session['domain'] = domain
  config.save()

  response_dict = {'domain': domain, 'credentials': config.credentials}
  response_json = json.dumps((response_dict))
  return flask.Response(ufo.XSSI_PREFIX + response_json,
                        headers=ufo.JSON_HEADERS)
