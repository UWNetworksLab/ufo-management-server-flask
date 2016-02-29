import flask
from mock import MagicMock
from mock import patch
from werkzeug import exceptions

from ufo import base_test
from ufo.services import error_handler
from ufo.services.custom_exceptions import SetupNeeded


class ErrorHandlerTest(base_test.BaseTest):
  """Test error handler class functionalities."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(ErrorHandlerTest, self).setUp()

  def testDefaultHTTPErrorHandlersAreRegistered(self):
    """Test the default HTTP error handlers are registered."""
    app_error_handlers = self.client.application.error_handler_spec[None]
    for error_code in exceptions.default_exceptions:
      self.assertTrue(error_code in app_error_handlers)

  def testUnknowExceptionTypesAreHandled(self):
    """Test that unknown exception types are handled (e.g. custom error).

    setup_config() is not called, thus SetupNeeded error should be thrown.
    """
    setup_needed_error = exceptions.InternalServerError(
        SetupNeeded.message)
    resp = self.client.get(flask.url_for('proxyserver_list'))

    self.assertTrue(str(setup_needed_error.code) in resp.data)
    self.assertTrue(setup_needed_error.name in resp.data)
    self.assertTrue(setup_needed_error.get_description() in resp.data)

  def testErrorHandlerCanProcessHTTPError(self):
    """Test error handler can process HTTP error."""
    error_404 = exceptions.NotFound()
    resp = error_handler.handle_error(error_404)

    self.assertTrue(str(error_404.code) in resp)
    self.assertTrue(error_404.name in resp)

  def testErrorHandlerCanProcessCustomError(self):
    """Test error handler can process custom error."""
    setup_needed_error = SetupNeeded()
    werkzeug_error = exceptions.InternalServerError(
        SetupNeeded.message)

    resp = error_handler.handle_error(setup_needed_error)

    self.assertTrue(str(werkzeug_error.code) in resp)
    self.assertTrue(werkzeug_error.name in resp)
    self.assertTrue(werkzeug_error.message in resp)


if __name__ == '__main__':
  unittest.main()
