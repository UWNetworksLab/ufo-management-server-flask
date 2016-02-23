"""User module which provides handlers to access and edit users."""
import ast
import base64
import flask
import json
import random

from googleapiclient import errors

from ufo import app
from ufo import db
from ufo import google_directory_service
from ufo import models
from ufo import oauth
from ufo import setup_required

INVITE_CODE_URL_PREFIX = 'https://uproxy.org/connect/#'


def _render_user_add(get_all, group_key, user_key):
  """Renders the user add template with the requested users if found.

  If users are found, they are stripped down to only their full name and
  email to avoid leaking unnecessary information. In the case that the
  users are not found, an empty list is used. If an httperror is
  encountered, that error is caught, and the template is still rendered
  with the error inserted and an empty list of users.

  Args:
    get_all: A boolean for whether or not to get all users in a domain.
    group_key: A string identifying a group of users and other groups.
    user_key: A string identifying an individual user.

  Returns:
    A rendered template of add_user.html with the users requested if found. If
    there is an error, that error is included in the template along with an
    empty list of users.
  """
  credentials = oauth.getSavedCredentials()
  # TODO this should handle the case where we do not have oauth
  if not credentials:
    return flask.render_template('add_user.html',
                                 directory_users=[],
                                 error="OAuth is not set up")

  try:
    directory_service = google_directory_service.GoogleDirectoryService(
        credentials)

    directory_users = []
    if get_all:
      directory_users = directory_service.GetUsers()
    elif group_key is not None and group_key is not '':
      directory_users = directory_service.GetUsersByGroupKey(group_key)
    elif user_key is not None and user_key is not '':
      directory_users = directory_service.GetUserAsList(user_key)

    users_to_output = []
    for directory_user in directory_users:
      user_for_display = {
          'name': directory_user['name']['fullName'],
          'email': directory_user['primaryEmail']
      }
      users_to_output.append(user_for_display)

    return flask.render_template('add_user.html',
                                 directory_users=users_to_output)
  except errors.HttpError as error:
    return flask.render_template('add_user.html',
                                 directory_users=[],
                                 error=error)

def _get_random_server_ip():
  """Gets the ip address of a random proxy server of those in the db.

  Returns:
    A randomly selected proxy server's ip address as a string.
  """
  proxy_servers = models.ProxyServer.query.all()
  if len(proxy_servers) == 0:
    return None

  index = random.randint(0, len(proxy_servers) - 1)
  return proxy_servers[index].ip_address

def _make_invite_code(user):
  """Create an invite code for the given user.

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
  ip = _get_random_server_ip()
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

@app.route('/user_json/')
@setup_required
def user_list_json():
  """Retrieves a list of the users currently in the db.

  Returns:
    A json object with 'users' set to the list of users in the db.
  """
  users = models.User.query.all()
  user_dict_list = []
  for user in users:
    user_dict_list.append(user.to_dict())
  users_json = json.dumps(({'users': user_dict_list}))
  return flask.Response(users_json, mimetype='application/json')

@app.route('/user/')
@setup_required
def user_list():
  """Renders the user list template with the users currently in the db.

  Returns:
    A rendered template of user.html with the users currently in the db.
  """
  users = models.User.query.all()
  user_emails = {}
  for user in users:
    user_emails[user.id] = user.email
  return flask.render_template('user.html',
                               user_payloads=user_emails)

@app.route('/user/add', methods=['GET', 'POST'])
@setup_required
def add_user():
  """Renders the user add template on get and stores new user(s) on post.

  This one handler does get and post for add user. The get method is handled
  by _render_user_add with the parameters for get_all, group_key, and user_key
  each passed along. The post method is handled here by inserting the new user
  or users into the database and redirecting to the user_list page.

  Returns:
    A rendered template of add_user.html with the requested users for a get or
    redirects to the user_list page after inserting users for a post.
  """
  if flask.request.method == 'GET':
    get_all = flask.request.args.get('get_all')
    group_key = flask.request.args.get('group_key')
    user_key = flask.request.args.get('user_key')
    return _render_user_add(get_all, group_key, user_key)

  json_users = flask.request.form.get('users')
  users_list = json.loads(json_users)
  for submitted_user in users_list:
    db_user = models.User()
    db_user.name = submitted_user['name']
    db_user.email = submitted_user['email']
    db_user.save(commit=False)

  if len(users_list) > 0:
    db.session.commit()

  return flask.redirect(flask.url_for('user_list'))

@app.route('/user/<user_id>/details')
@setup_required
def user_details(user_id):
  """Renders the user details template for the given user_id if found.

  If the user is not found, this produces a 404 error which redirects to the
  error handler.

  Args:
    user_id: A string identifying a user in the database.

  Returns:
    A rendered template of user_details.html for the given user_id along with
    an invite code for that user if available.
  """
  user = models.User.query.get_or_404(user_id)
  invite_code = _make_invite_code(user)
  if invite_code is None:
    return flask.render_template('user_details.html', user=user)
  else:
    invite_url = INVITE_CODE_URL_PREFIX + invite_code
    return flask.render_template('user_details.html', user=user,
                                 invite_url=invite_url)

@app.route('/user/<user_id>/delete', methods=['POST'])
@setup_required
def delete_user(user_id):
  """Deletes the user corresponding to the passed in user_id from the db.

  If we had access to a delete method then we would not use get here.
  If the user is not found, this produces a 404 error which redirects to the
  error handler.

  Args:
    user_id: A string identifying a user in the database.

  Returns:
    A redirect to the user_list page after deleting the given user.
  """
  user = models.User.query.get_or_404(user_id)
  user.delete()

  return flask.redirect(flask.url_for('user_list'))

@app.route('/user/<user_id>/getNewKeyPair', methods=['POST'])
@setup_required
def user_get_new_key_pair(user_id):
  """Rotates the key pair (public and private keys) for the given user.

  If the user is not found, this produces a 404 error which redirects to the
  error handler.

  Args:
    user_id: A string identifying a user in the database.

  Returns:
    A redirect to the user_details page after rotating the user's keys.
  """
  user = models.User.query.get_or_404(user_id)
  user.regenerate_key_pair()
  user.save()

  return flask.redirect(flask.url_for('user_details', user_id=user_id))

@app.route('/user/<user_id>/toggleRevoked', methods=['POST'])
@setup_required
def user_toggle_revoked(user_id):
  """Toggles whether the given user's access is revoked or not.

  If the user is not found, this produces a 404 error which redirects to the
  error handler.

  Args:
    user_id: A string identifying a user in the database.

  Returns:
    A redirect to the user_details page after flipping is_key_revoked.
  """
  user = models.User.query.get_or_404(user_id)
  user.is_key_revoked = not user.is_key_revoked
  user.save()

  return flask.redirect(flask.url_for('user_details', user_id=user_id))
