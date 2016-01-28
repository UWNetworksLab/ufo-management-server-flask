"""An error handler module to gracefully handle all application errors.

The work here is based on the most-excellent flask development doc below.
https://goo.gl/OWOa70

One difference here is that we will aim to handle custom exceptions.
"""
import logging

from flask import render_template
from flask import request
from werkzeug import exceptions


def handle_error(error):
  """A handler to gracefully handle any application errors.

  Args:
    error: Exception object, either python or werkzeug.
  """
  logging.error('Request resulted in {}'.format(error))

  if not isinstance(error, exceptions.HTTPException):
    error = exceptions.InternalServerError(error.message)
  
  # Flask supports looking up multiple templates and rendering the first
  # one it finds.  This will let us create specific error pages
  # for errors where we can provide the user some additional help.
  # (Like a 404, for example).
  templates_to_try = ['{}_error.html'.format(error.code), 'error.html']
  return render_template(templates_to_try, error=error)

def init_error_handlers(app):
  """Register all the default HTTP error handlers with flask.

  Args:
    app: flask app object
  """

  for exception in exceptions.default_exceptions:
    app.register_error_handler(exception, handle_error)
  app.register_error_handler(Exception, handle_error)
