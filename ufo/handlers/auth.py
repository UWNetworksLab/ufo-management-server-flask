"""Auth module which provides login handlers and decorators."""

import json

import flask
import functools

import ufo
from ufo.database import models
from ufo.services.custom_exceptions import NotLoggedIn


# TODO(eholder): Add functional or unit tests for each decorator.
def is_user_logged_in():
  """Checks whether or not a user is logged in currently.

  Returns:
    True when a user is logged into the current session. False otherwise.
  """
  if 'email' not in flask.session:
    return False

  user = models.AdminUser.get_by_email(flask.session['email'])
  return user is not None

def login_required(f):
  """Requires that the user be logged in to access the page.

  Args:
    f: The function being decorated.

  Returns:
    A call to the decorated function if the user is logged in.

  Raises:
    NotLoggedIn: If the user is not logged in currently.
  """
  @functools.wraps(f)
  def decorated(*args, **kwargs):
    """Requires that the user be logged in to access the page.

    Returns:
      A call to the decorated function if the user is logged in.

    Raises:
      NotLoggedIn: If the user is not logged in currently.
    """
    if not is_user_logged_in():
      raise NotLoggedIn

    return f(*args, **kwargs)

  return decorated

def login_required_if_setup(f):
  """Requires that the user be logged in if the setup process has finished.

  Args:
    f: The function being decorated.

  Returns:
    A call to the decorated function if the setup process is incomplete or
    a user is logged in.

  Raises:
    NotLoggedIn: If the setup process is complete and a user is not logged in
    currently.
  """
  @functools.wraps(f)
  def decorated(*args, **kwargs):
    """Requires that the user be logged in if the setup process has finished.

    Returns:
      A call to the decorated function if the setup process is incomplete or
      a user is logged in.

    Raises:
      NotLoggedIn: If the setup process is complete and a user is not logged in
      currently.
    """
    config = ufo.get_user_config()
    if not config.isConfigured:
      return f(*args, **kwargs)

    if is_user_logged_in():
      return f(*args, **kwargs)

    raise NotLoggedIn

  return decorated

@ufo.app.route('/login/', methods=['GET', 'POST'])
def login():
  """Logs a user into the management server.

  Returns:
    A redirect to the login page if there is any problem with the current user
    or a redirect to the landing page if everything checks out.
  """
  if is_user_logged_in():
    return flask.redirect(flask.url_for('landing'))

  if flask.request.method == 'GET':
    return flask.render_template('login.html',
                                 error=flask.request.form.get('error'))

  email = flask.request.form.get('email')
  password = flask.request.form.get('password')

  user = models.AdminUser.get_by_email(email)
  if user is None:
    return flask.redirect(flask.url_for('login', error='No valid user found.'))

  if not ufo.RECAPTCHA.verify():
    return flask.redirect(flask.url_for('login', error='Failed recaptcha.'))

  if not user.does_password_match(password):
    return flask.redirect(flask.url_for('login', error='Invalid password.'))

  flask.session['email'] = user.email

  return flask.redirect(flask.url_for('landing'))

@ufo.app.route('/logout/', methods=['POST'])
def logout():
  """Logs the current user out, redirects to login.

  Returns:
    A redirect to the login page.
  """
  flask.session.pop('email', None)

  return flask.redirect(flask.url_for('login'))
