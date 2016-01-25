"""Test user page module functionality."""
import unittest

from base_test import BaseTest
from test_config import CHROME_DRIVER_LOCATION
from ufo import app
from user_page import UserPage

import flask
from selenium import webdriver


class UserPageTest(BaseTest):

  """Test user page functionality."""

  def setUp(self):
    """Setup for test methods."""
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    # TODO(eholder) Re-enable this once we have a login module again.
    # LoginPage(self.driver).Login(self.args)
    self.context = app.test_request_context()
    self.context.push()

  def testUserPage(self):
    """Test the user page."""
    # TODO(eholder): Improve the checks here to be based on something more
    # robust, such as the presence of element id's or that the page renders
    # as expected, since this text can change in the future and is not i18ned.
    add_users = (u'Add Users').upper()

    self.driver.get(self.args.server_url + flask.url_for('user_list'))
    user_page = UserPage(self.driver)
    self.assertEquals(add_users, user_page.GetAddUserLink().text)
    self.assertIsNotNone(user_page.GetSidebar())

  def tearDown(self):
    """Teardown for test methods."""
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
