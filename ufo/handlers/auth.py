"""Auth module which provides login handlers and decorators."""

import datetime
import json

import flask
import functools

import ufo
from ufo.database import models
from ufo.services.custom_exceptions import NotLoggedIn

MAX_FAILED_LOGINS_BEFORE_RECAPTCHA = 10
INITIAL_RECAPTCHA_TIMEFRAME_MINUTES = 2


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
    return _handle_login_get()

  email = flask.request.form.get('email')
  password = flask.request.form.get('password')

  user = models.AdminUser.get_by_email(email)
  if user is None:
    return flask.redirect(flask.url_for('login', error='No valid user found.'))

  config = ufo.get_user_config()
  if config.should_show_recaptcha and not ufo.RECAPTCHA.verify():
    models.FailedLoginAttempt.create()
    return flask.redirect(flask.url_for('login', error='Failed recaptcha.'))

  if not user.does_password_match(password):
    models.FailedLoginAttempt.create()
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

def _handle_login_get():
  """Determines whether or not to show the recaptcha and serves the login page.

  Return:
    A rendered login page template possibly with or without recaptcha.
  """
  should_show_recaptcha, failed_attempts_count = determine_if_recaptcha_should_be_turned_on_or_off()

  flask.session['failures'] = failed_attempts_count
  flask.session['should_show_recaptcha'] = should_show_recaptcha
  return flask.render_template('login.html',
                               error=flask.request.form.get('error'))


def determine_if_recaptcha_should_be_turned_on_or_off():
  """Determines whether or not to show the recaptcha and updates the DB.

  Return:
    A tuple where the first entry is a boolean for whether or not to show
    recaptcha and the second entry is the count of failed login attempts.
  """
  config = ufo.get_user_config()
  failed_attempts_count = 0
  now = datetime.datetime.now()

  if config.should_show_recaptcha:
    failed_attempts_count = models.FailedLoginAttempt.count_since_datetime(
        config.recaptcha_start_datetime)
    if config.recaptcha_end_datetime < now:
      # This is the case when the recaptcha was on and timed out so turn it off
      config.should_show_recaptcha = False
      models.FailedLoginAttempt.delete_before_datetime(
          config.recaptcha_end_datetime)
    elif failed_attempts_count >= MAX_FAILED_LOGINS_BEFORE_RECAPTCHA:
      # This is the case when the recaptcha was on and has since seen more
      # failures over the threshold, so it needs to be extended.
      delta = (
          config.recaptcha_end_datetime - config.recaptcha_start_datetime)
      _turn_on_recaptcha(config, now, delta * 2)
  else:
    delta = datetime.timedelta(minutes=INITIAL_RECAPTCHA_TIMEFRAME_MINUTES)
    failed_attempts_count = models.FailedLoginAttempt.count_since_datetime(
        now - delta)
    if failed_attempts_count >= MAX_FAILED_LOGINS_BEFORE_RECAPTCHA:
      # This is the case when I need to turn on recaptcha initially.
      _turn_on_recaptcha(config, now, delta)

  config.save()
  return config.should_show_recaptcha, failed_attempts_count

def _turn_on_recaptcha(config, current_datetime, length_of_recaptcha):
  """Turn on recaptcha in the configuration object.

  Args:
    config: The configuration object from the database which turns on recaptcha
    current_datetime: The current datetime for the start of recaptcha.
    length_of_recaptcha: A timedelta for how long recaptcha should last.
  """
  config.should_show_recaptcha = True
  config.recaptcha_start_datetime = current_datetime
  config.recaptcha_end_datetime = current_datetime + length_of_recaptcha
