"""Test base module functionality."""

import unittest

from test_config import CHROME_DRIVER_LOCATION
from ufo import app

from selenium import webdriver

class BaseTest(unittest.TestCase):

  """Base test class to inherit from."""

  def __init__(self, methodName='runTest', args=None, **kwargs):
    """Create the base test object for others to inherit."""
    super(BaseTest, self).__init__(methodName, **kwargs)
    self.args = args

  def setUp(self):
    """Setup for test methods."""
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    # TODO(eholder) Re-enable this once we have a login module again.
    # LoginPage(self.driver).Login(self.args)

  def setContext(self):
    """Set context as test_request_context so we can use flask.url_for."""
    self.context = app.test_request_context()
    self.context.push()

  def tearDown(self):
    """Teardown for test methods."""
    self.driver.quit()
