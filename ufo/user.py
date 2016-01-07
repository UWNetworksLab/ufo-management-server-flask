from . import app, db, setup_required

import ast
import base64
import flask
import google_directory_service
import json
import models
import oauth
import random

from googleapiclient import errors

def _RenderUserAdd():
  get_all = flask.request.args.get('get_all')
  group_key = flask.request.args.get('group_key')
  user_key = flask.request.args.get('user_key')

  credentials = oauth.getSavedCredentials()
  # TODO this should handle the case where we do not have oauth
  if not credentials:
    return flask.render_template('add_user.html',
                                 directory_users=[],
                                 error="OAuth is not set up")

  try:
    directory_service = google_directory_service.GoogleDirectoryService(credentials)

    directory_users = []
    if get_all:
      directory_users = directory_service.GetUsers()
    elif group_key is not None and group_key is not '':
      directory_users = directory_service.GetUsersByGroupKey(group_key)
    elif user_key is not None and user_key is not '':
      directory_users = directory_service.GetUserAsList(user_key)

    return flask.render_template('add_user.html',
                                 directory_users=directory_users)
  except errors.HttpError as error:
    return flask.render_template('add_user.html',
                                 directory_users=[],
                                 error=error)

def _GetRandomServerIp():
  proxy_servers = models.ProxyServer.query.all()
  if len(proxy_servers) == 0:
    return None

  index = random.randint(0, len(proxy_servers) - 1)
  return proxy_servers[index].ip_address

def _MakeInviteCode(user):
  r"""Create an invite code for the given user.

  The invite code is a format created by the uproxy team.
  Below is an example of an unencoded invite code for a cloud instance:

  {
    "networkName": "Cloud",
    "networkData": "{
      \"host\":\"178.62.123.172\",
      \"user\":\"giver\",
      \"key\":\"base64_key"
    }"
  }

  It includes the host ip (of the proxy server or load balancer) to connect
  the user to, the user username (user's email) to connect with, and
  the credential (private key) necessary to authenticate with the host.

  TODO: Guard against any future breakage when the invite code format
  is changed again.  Possibly adding a test on the uproxy-lib side
  to fail and point to updating this here.

  Args:
    user: A user from the datastore to generate an invite code for.

  Returns:
    invite_code: A base64 encoded dictionary of host, user, and pass which
    correspond to the proxy server/load balancer's ip, the user's email, and
    the user's private key, respectively.  See example above.
  """
  ip = _GetRandomServerIp()
  if ip is None:
    return None

  invite_code_data = {
      'networkName': 'Cloud',
      'networkData': {
        'host': ip,
        'user': user.email,
        'pass': user.private_key,
      },
  }
  json_data = json.dumps(invite_code_data)
  invite_code = base64.urlsafe_b64encode(json_data)

  return invite_code

@app.route('/user/')
@setup_required
def user_list():
  users = models.User.query.all()
  user_emails = {}
  for user in users:
    user_emails[user.id] = user.email
  return flask.render_template('user.html',
                               user_payloads=user_emails)

@app.route('/user/add', methods=['GET', 'POST'])
@setup_required
def add_user():
  if flask.request.method == 'GET':
    return _RenderUserAdd()

  users = flask.request.form.getlist('selected_user')
  decoded_users = []
  for user in users:
    # TODO we should be submitting data in a better format
    u = ast.literal_eval(user)
    user = models.User()
    user.name = u['name']['fullName']
    user.email = u['primaryEmail']
    db.session.add(user)

  return flask.redirect(flask.url_for('user_list'))

@app.route('/user/<user_id>/details')
@setup_required
def user_details(user_id):
  user = models.User.query.get_or_404(user_id)
  return flask.render_template('user_details.html',
                               user=user,
                               invite_code=_MakeInviteCode(user))

@app.route('/user/<user_id>/delete')
@setup_required
def delete_user(user_id):
  """Delete the user corresponding to the passed in key.

  If we had access to a delete method then we would not use get here.
  """
  #TODO guess what the comment is?  Yup, should be a post.
  user = models.User.query.get_or_404(user_id)

  db.session.delete(user)

  return flask.redirect(flask.url_for('user_list'))

@app.route('/user/<user_id>/getNewKeyPair')
@setup_required
def user_get_new_key_pair(user_id):
  #TODO yeah...should be post at least
  user = models.User.query.get_or_404(user_id)
  user.regenerate_key_pair()

  return flask.redirect(flask.url_for('user_details', user_id=user_id))

@app.route('/user/<user_id>/toggleRevoked')
@setup_required
def user_toggle_revoked(user_id):
  # TODO the toggle alone means this should be a post!
  user = models.User.query.get_or_404(user_id)
  user.is_key_revoked = not user.is_key_revoked

  return flask.redirect(flask.url_for('user_details', user_id=user_id))
