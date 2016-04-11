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
    super(ErrorHandlerTest, self).setup_auth()

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
    self.assertTrue(SetupNeeded.message in resp.data)

  def testErrorHandlerCanProcessInternalServerError(self):
    """Test error handler can process HTTP error."""
    error_500 = exceptions.InternalServerError()
    resp = error_handler.handle_error(error_500)

    self.assertEqual(error_500.code, resp[1])
    self.assertTrue(str(error_500.code) in resp[0].data)
    self.assertTrue(error_500.message in resp[0].data)

  def ErrorHandlerCanProcessCustomError(self):
    """Test error handler can process custom error."""
    setup_needed_error = SetupNeeded()
    werkzeug_error = exceptions.InternalServerError(
        SetupNeeded.message)

    resp = error_handler.handle_error(setup_needed_error)

    self.assertEqual(werkzeug_error.code, resp[1])
    self.assertTrue(str(werkzeug_error.code) in resp[0].data)
    self.assertTrue(werkzeug_error.message in resp[0].data)

  # TODO(eholder): Add a test for the not logged in error handler.


if __name__ == '__main__':
  unittest.main()
