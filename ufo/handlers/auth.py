import flask
import functools

import ufo
from ufo.database import models


class NotLoggedIn(Exception):
  code = 401
  message = 'User is not logged in'

def is_user_logged_in():
  if 'username' not in flask.session:
    return False

  user = models.ManagementServerUser.get_by_username(flask.session['username'])
  return user is not None

def login_required(f):
  """Requires that the user be logged in to access the page.
  """
  @functools.wraps(f)
  def decorated(*args, **kwargs):
    if not is_user_logged_in():
      raise NotLoggedIn

    return f(*args, **kwargs)

  return decorated

def login_required_if_setup(f):
  """Requires that the user be logged in if the setup process has finished.
  """
  @functools.wraps(f)
  def decorated(*args, **kwargs):
    config = ufo.get_user_config()
    if (not config.isConfigured) or is_user_logged_in():
      return f(*args, **kwargs)

    raise NotLoggedIn

  return decorated

@ufo.app.route('/login/', methods=['GET', 'POST'])
def login():
  """Logs a user into the management server."""
  if flask.request.method == 'GET':
    return flask.render_template('login.html',
                                 error=flask.request.form.get('error'))

  username = flask.request.form.get('username')
  password = flask.request.form.get('password')

  user = models.ManagementServerUser.get_by_username(username)
  if user is None:
    return flask.redirect(flask.url_for('login', error='No valid user found'))

  if not user.check_password(password):
    return flask.redirect(flask.url_for('login', error='Invalid password'))

  flask.session['username'] = user.username

  return flask.redirect(flask.url_for('landing'))

@ufo.app.route('/logout/', methods=['GET', 'POST'])
def logout():
  """Logs the current user out, redirects to login.

  Responds to get and post requests for now...really should only be post.
  """
  flask.session.pop('username', None)

  return flask.redirect(flask.url_for('login'))
