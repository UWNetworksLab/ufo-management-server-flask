"""Test error notification functionalities."""
import unittest

import flask
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base_test import BaseTest
from error_notification import ErrorNotification
from login_page import LoginPage
from landing_page import LandingPage
from ufo.services import custom_exceptions


class ErrorNotificationTest(BaseTest):
  """Tests for error notifications."""

  def setUp(self):
    """Setup for test methods."""
    super(ErrorNotificationTest, self).setUp()
    super(ErrorNotificationTest, self).set_context()
    LoginPage(self.driver).Login(self.args.server_url, self.args.email,
                                 self.args.password)

  def tearDown(self):
    """Teardown for test methods."""
    landing_page = LandingPage(self.driver)
    landing_page.removeTestUser(BaseTest.TEST_USER_AS_DICT['name'],
                                self.args.server_url,
                                should_raise_exception=False)
    LoginPage(self.driver).Logout(self.args.server_url)
    super(ErrorNotificationTest, self).tearDown()

  def testErrorNotificationIsWorking(self):
    """Test the error notification is properly wired up, opened, and closed.

    Not testing the actual behavior directly (e.g. the db save) as those should
    be covered by unit tests.
    """
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)

    # By default the error notification will be present but not displayed.
    error_notification = ErrorNotification(self.driver)
    self.assertTrue(error_notification.is_present())
    self.assertFalse(error_notification.is_displayed())

    landing_page.add_test_user(BaseTest.TEST_USER_AS_DICT['name'],
                               BaseTest.TEST_USER_AS_DICT['email'],
                               self.args.server_url)
    landing_page.add_test_user(BaseTest.TEST_USER_AS_DICT['name'],
                               BaseTest.TEST_USER_AS_DICT['email'],
                               self.args.server_url)

    # Trying to add the same user twice will cause the error notification
    # to be displayed.
    WebDriverWait(self.driver, ErrorNotification.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located((
            error_notification.ERROR_NOTIFICATION_DIALOG)))
    self.assertTrue(error_notification.is_displayed())

    # Check the correct error message is displayed.
    # TODO: Make it testable for i18n.
    message = custom_exceptions.UnableToSaveToDB.message
    self.assertTrue(error_notification.has_error_message(message))

    # Check we can close the error notification.
    error_notification.close()
    self.assertFalse(error_notification.is_displayed())


if __name__ == '__main__':
  unittest.main()
