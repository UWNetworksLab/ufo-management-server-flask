"""An error handler module to gracefully handle all application errors.

The work here is based on the most-excellent flask development doc below.
https://goo.gl/OWOa70

One difference here is that we will aim to handle custom exceptions.
"""
import logging

import flask
from werkzeug import exceptions

from ufo.handlers import auth

def handle_error(error):
  """A handler to gracefully handle any application errors.

  Args:
    error: Exception object, either python or werkzeug.

  Returns:
    A redirect to one of the templates found along with the specified error
    as text on the page.
  """
  logging.error('Request resulted in {}'.format(error))

  if not isinstance(error, exceptions.HTTPException):
    error = exceptions.InternalServerError(error.message)

  return flask.jsonify({'code': error.code,
                        'message': error.description}), error.code

def handle_not_logged_in(error):
  """A handler to gracefully handle the not logged in error.

  Args:
    error: The not logged in exception.

  Returns:
    A redirect to the login page.
  """
  return flask.redirect(flask.url_for('login'))

def init_error_handlers(app):
  """Register all the default HTTP error handlers with flask.

  Args:
    app: flask app object
  """

  for exception in exceptions.default_exceptions:
    app.register_error_handler(exception, handle_error)
  app.register_error_handler(auth.NotLoggedIn, handle_not_logged_in)
  app.register_error_handler(Exception, handle_error)
