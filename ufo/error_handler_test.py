from mock import MagicMock
from mock import patch

import base_test
import error_handler
from setup import SetupNeeded

import flask
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import NotFound


class ErrorHandlerTest(base_test.BaseTest):
  """Test error handler class functionalities."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(ErrorHandlerTest, self).setUp()

  def testDefaultHTTPErrorHandlersAreRegistered(self):
    """Test the default HTTP error handlers are registered."""
    app_error_handlers = self.client.application.error_handler_spec[None]
    for error_code in default_exceptions:
      self.assertTrue(error_code in app_error_handlers)

  def testCustomErrorIsHandled(self):
    """Test custom error handler is registered.
    
    setup_config() is not called, thus SetupNeeded error should be thrown.
    TODO(henry): see if this should be moved to setup_test.py
    """
    resp = self.client.get(flask.url_for('proxyserver_list'))

    self.assertTrue(error_handler.ERROR_CODE_500 in resp.data)
    self.assertTrue(error_handler.ERROR_NAME_500 in resp.data)
    self.assertTrue(SetupNeeded.message in resp.data)

  def testErrorHandlerCanProcessHTTPError(self):
    """Test error handler can process HTTP error."""
    error_404 = NotFound()
    resp = error_handler.handle_error(error_404)

    self.assertTrue(str(error_404.code) in resp)
    self.assertTrue(error_404.name in resp)

  def testErrorHandlerCanProcessCustomError(self):
    """Test error handler can process custom error."""
    setup_needed = SetupNeeded()
    resp = error_handler.handle_error(setup_needed)

    self.assertTrue(error_handler.ERROR_CODE_500 in resp)
    self.assertTrue(error_handler.ERROR_NAME_500 in resp)
    self.assertTrue(setup_needed.message in resp)


if __name__ == '__main__':
  unittest.main()
