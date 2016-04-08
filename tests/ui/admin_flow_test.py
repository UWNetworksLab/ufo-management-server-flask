"""Test admin flows."""
import unittest

import flask
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from admin_flow import AdminFlow
from base_test import BaseTest
from login_page import LoginPage


class AdminFlowTest(BaseTest):

  """Test admin flows."""
  TEST_ADMIN_AS_DICT = {
      'username': 'Test Admin Fake Name 01',
      'password': 'fake admin password that could be anything'
  }

  def setUp(self):
    """Setup for test methods."""
    super(AdminFlowTest, self).setUp()
    super(AdminFlowTest, self).setContext()

  def tearDown(self):
    """Teardown for test methods."""
    admin_flow = AdminFlow(self.driver)
    LoginPage(self.driver).Login(self.args.server_url, self.args.username,
                                 self.args.password)
    admin_flow.removeTestAdmin(self.TEST_ADMIN_AS_DICT['username'],
                               self.args.server_url,
                               should_raise_exception=False)
    LoginPage(self.driver).Logout(self.args.server_url)
    super(AdminFlowTest, self).tearDown()

  def testAddingAnotherAdminWorks(self):
    """Test that adding another admin works and lets us login as that admin."""
    admin_flow = AdminFlow(self.driver)
    for handler in self.handlers:
      self._verifyAnotherAdminCanBeAdded(self.args.server_url + handler)
      admin_flow.removeTestAdmin(self.TEST_ADMIN_AS_DICT['username'],
                                 self.args.server_url,
                                 should_raise_exception=False)
      LoginPage(self.driver).Logout(self.args.server_url)

  def testRemovingAdminWorks(self):
    """Test that removing an admin works."""
    for handler in self.handlers:
      self._verifyAdminCanBeRemoved(self.args.server_url + handler)
      LoginPage(self.driver).Logout(self.args.server_url)

  def testAdminUsernameIsDisplayed(self):
    """Test that the admin's username is displayed while logged in."""
    LoginPage(self.driver).Login(self.args.server_url, self.args.username,
                                 self.args.password)
    for handler in self.handlers:
      self.driver.get(self.args.server_url + handler)
      dropdown_button = self.driver.find_element(*AdminFlow.OPEN_MENU_BUTTON)
      self.assertEquals(dropdown_button.text.lower(),
                        self.args.username.lower())
    LoginPage(self.driver).Logout(self.args.server_url)

  def _verifyAnotherAdminCanBeAdded(self, test_url):
    """Test that adding another admin works from the given url.

    Args:
      test_url: The url to add the admin from.
    """
    # Try to login with the uncreated admin to ensure it does not exist.
    with self.assertRaises(TimeoutException):
      LoginPage(self.driver).Login(self.args.server_url,
                                   self.TEST_ADMIN_AS_DICT['username'],
                                   self.TEST_ADMIN_AS_DICT['password'])
    self.driver.get(test_url)

    # Assert that login failed (we're still on the login page).
    login_url = self.args.server_url + flask.url_for('login')
    self.assertEquals(login_url, self.driver.current_url)

    # Login as an existing admin to get access.
    LoginPage(self.driver).Login(self.args.server_url, self.args.username,
                                 self.args.password)
    self.driver.get(test_url)

    # Find the add admin dialog.
    admin_flow = AdminFlow(self.driver)
    dropdown_menu = admin_flow.getDropdownMenu()
    add_admin_dialog = admin_flow.getAddAdminDialog(dropdown_menu)
    with self.assertRaises(NoSuchElementException):
      response_status = add_admin_dialog.find_element(
          *AdminFlow.ADD_ADMIN_RESPONSE_STATUS)
      self.assertIsNone(response_status)

    # Add the new admin.
    admin_flow.addTestAdmin(self.TEST_ADMIN_AS_DICT['username'],
                            self.TEST_ADMIN_AS_DICT['password'],
                            add_admin_dialog)

    # Assert that it worked.
    response_status = add_admin_dialog.find_element(
        *AdminFlow.ADD_ADMIN_RESPONSE_STATUS)
    self.assertIsNotNone(response_status)

    # Logout of the existing admin account.
    LoginPage(self.driver).Logout(self.args.server_url)

    # Login as the newly created test admin.
    LoginPage(self.driver).Login(self.args.server_url,
                                 self.TEST_ADMIN_AS_DICT['username'],
                                 self.TEST_ADMIN_AS_DICT['password'])
    self.driver.get(test_url)

    # Assert that login succeeded (we're now on the test_url page).
    self.assertEquals(test_url, self.driver.current_url)

  def _verifyAdminCanBeRemoved(self, test_url):
    """Test that removing an admin works from the given url.

    Args:
      test_url: The url to remove the admin from.
    """
    # Login as an existing admin to get access.
    LoginPage(self.driver).Login(self.args.server_url, self.args.username,
                                 self.args.password)
    self.driver.get(test_url)

    # Find the add admin dialog.
    admin_flow = AdminFlow(self.driver)
    dropdown_menu = admin_flow.getDropdownMenu()
    add_admin_dialog = admin_flow.getAddAdminDialog(dropdown_menu)

    # Add the test admin.
    admin_flow.addTestAdmin(self.TEST_ADMIN_AS_DICT['username'],
                            self.TEST_ADMIN_AS_DICT['password'],
                            add_admin_dialog)

    # Remove the test admin.
    admin_flow.removeTestAdmin(self.TEST_ADMIN_AS_DICT['username'],
                               self.args.server_url,
                               should_raise_exception=True)

    # See if the admin exists.
    self.driver.get(test_url)
    dropdown_menu = admin_flow.getDropdownMenu()
    remove_admin_dialog = admin_flow.getRemoveAdminDialog(dropdown_menu)
    remove_admin_form = remove_admin_dialog.find_element(
        *AdminFlow.REMOVE_ADMIN_FORM)
    admin_item = admin_flow.findTestAdminOnRemoveForm(
        self.TEST_ADMIN_AS_DICT['username'], remove_admin_form)

    self.assertIsNone(admin_item)


if __name__ == '__main__':
  unittest.main()
