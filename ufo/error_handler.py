"""An error handler module to gracefully handle all application errors.

The work here is based on the most-excellent flask development doc below.
https://goo.gl/OWOa70

One difference here is that we will aim to handle custom exceptions.
"""

from flask import current_app
from flask import Markup
from flask import render_template
from flask import request
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException


ERROR_CODE_500 = '500'
ERROR_NAME_500 = 'Internal Server Error'


def handle_error(error):
  """A handler to gracefully handle any application errors.
  
  Args:
    error: Exception object, either python or werkzeug.
  """
  message = 'Request resulted in {}'.format(error)
  current_app.logger.error(message, exc_info=error)

  if isinstance(error, HTTPException):
    error_code = error.code
    error_name = error.name
    error_text = error.get_description(request.environ)
  else:
    error_code = ERROR_CODE_500
    error_name = ERROR_NAME_500
    error_text = error.message

  # Flask supports looking up multiple templates and rendering the first
  # one it finds.  This will let us create specific error pages
  # for errors where we can provide the user some additional help.
  # (Like a 404, for example).
  templates_to_try = ['{}_error.html'.format(error_code),
                      'error.html']
  return render_template(templates_to_try,
                         error_code=error_code,
                         error_name=error_name,
                         error_text=Markup(error_text))

def init_error_handlers(app):
  """Register all the default HTTP error handlers with flask.
  
  Args:
    app: flask app object
  """

  for exception in default_exceptions:
    app.register_error_handler(exception, handle_error)
  app.register_error_handler(Exception, handle_error)
