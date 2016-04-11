"""Test for undefined URL.

When user is trying to access undefined url, we will show the error page
instead of the error notification, which is preferred but is not easily done
at this point.
"""
import unittest

import flask
from selenium.webdriver.support import expected_conditions as EC
from werkzeug import exceptions

from base_test import BaseTest
from error_page import ErrorPage

class UndefinedURLTest(BaseTest):
  """Tests for undefined URL."""

  def setUp(self):
    """Setup for test methods."""
    super(UndefinedURLTest, self).setUp()

  def tearDown(self):
    """Teardown for test methods."""
    super(UndefinedURLTest, self).tearDown()

  def testErrorPageIsRenderedForUndefinedURL(self):
    """Test that error page is shown for undefined URL."""
    self.driver.get(self.args.server_url + '/foobar123')

    error_code_element = self.driver.find_element(
        *ErrorPage.ERROR_CODE_ELEMENT)
    error_description_element = self.driver.find_element(
        *ErrorPage.ERROR_DESCRIPTION_ELEMENT)

    error_404 = exceptions.NotFound()

    self.assertEquals('Error ' + str(error_404.code),
                      error_code_element.text)

    self.assertEquals(error_404.description.replace('  ', ' '),
                      error_description_element.text.encode('ascii'))


if __name__ == '__main__':
  unittest.main()
