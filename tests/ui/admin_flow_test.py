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
      'email': 'test_admin_fake_name_01@fake.com',
      'password': 'fake admin password that could be anything',
      'new_password': 'fake admin password different from the first'
  }

  def setUp(self):
    """Setup for test methods."""
    super(AdminFlowTest, self).setUp()
    super(AdminFlowTest, self).set_context()

  def tearDown(self):
    """Teardown for test methods."""
    admin_flow = AdminFlow(self.driver)
    LoginPage(self.driver).Login(self.args.server_url, self.args.email,
                                 self.args.password)
    admin_flow.remove_test_admin(self.TEST_ADMIN_AS_DICT['email'],
                                 self.args.server_url,
                                 should_raise_exception=False)
    LoginPage(self.driver).Logout(self.args.server_url)
    super(AdminFlowTest, self).tearDown()

  def testAddingAnotherAdminWorks(self):
    """Test that adding another admin works and lets us login as that admin."""
    admin_flow = AdminFlow(self.driver)
    for handler in self.handlers:
      self.assertAnotherAdminCanBeAdded(self.args.server_url + handler)
      admin_flow.remove_test_admin(self.TEST_ADMIN_AS_DICT['email'],
                                   self.args.server_url,
                                   should_raise_exception=False)
      LoginPage(self.driver).Logout(self.args.server_url)

  def testChangingAdminPasswordWorks(self):
    """Test that changing an admin's password works."""
    LoginPage(self.driver).Login(self.args.server_url, self.args.email,
                                 self.args.password)
    test_url = self.args.server_url + flask.url_for('landing')
    self.driver.get(test_url)

    # Find the add admin dialog.
    admin_flow = AdminFlow(self.driver)
    dropdown_menu = admin_flow.getDropdownMenu()
    add_admin_dialog = admin_flow.get_add_admin_dialog(dropdown_menu)

    # Add the test admin.
    admin_flow.add_test_admin(self.TEST_ADMIN_AS_DICT['email'],
                              self.TEST_ADMIN_AS_DICT['password'],
                              add_admin_dialog)
    admin_flow.close_dropdown_menu_from_dialog(add_admin_dialog)

    # Logout of the existing admin account.
    LoginPage(self.driver).Logout(self.args.server_url)

    # Login as the newly created test admin.
    LoginPage(self.driver).Login(self.args.server_url,
                                 self.TEST_ADMIN_AS_DICT['email'],
                                 self.TEST_ADMIN_AS_DICT['password'])

    self.driver.get(test_url)
    dropdown_menu = admin_flow.getDropdownMenu()
    change_admin_password_dialog = admin_flow.get_change_password_dialog(
        dropdown_menu)

    # Change the test admin's password.
    admin_flow.change_admin_password(self.TEST_ADMIN_AS_DICT['password'],
                                     self.TEST_ADMIN_AS_DICT['new_password'],
                                     change_admin_password_dialog)

    # Logout of the existing admin account.
    LoginPage(self.driver).Logout(self.args.server_url)

    # Login with the new credentials.
    LoginPage(self.driver).Login(self.args.server_url,
                                 self.TEST_ADMIN_AS_DICT['email'],
                                 self.TEST_ADMIN_AS_DICT['new_password'])

    # Assert that login succeeded (we're now on the test_url page).
    self.assertEquals(test_url, self.driver.current_url)

    LoginPage(self.driver).Logout(self.args.server_url)

  def testRemovingAdminWorks(self):
    """Test that removing an admin works."""
    for handler in self.handlers:
      self.assertAdminCanBeRemoved(self.args.server_url + handler)
      LoginPage(self.driver).Logout(self.args.server_url)

  def testAdminEmailIsDisplayed(self):
    """Test that the admin's email is displayed while logged in."""
    LoginPage(self.driver).Login(self.args.server_url, self.args.email,
                                 self.args.password)
    for handler in self.handlers:
      self.driver.get(self.args.server_url + handler)
      dropdown_button = self.driver.find_element(*AdminFlow.OPEN_MENU_BUTTON)
      self.assertEquals(dropdown_button.text.lower(),
                        self.args.email.lower())
    LoginPage(self.driver).Logout(self.args.server_url)

  def assertAnotherAdminCanBeAdded(self, test_url):
    """Test that adding another admin works from the given url.

    Args:
      test_url: The url to add the admin from.
    """
    # Try to login with the uncreated admin to ensure it does not exist.
    with self.assertRaises(TimeoutException):
      LoginPage(self.driver).Login(self.args.server_url,
                                   self.TEST_ADMIN_AS_DICT['email'],
                                   self.TEST_ADMIN_AS_DICT['password'])
    self.driver.get(test_url)

    # Assert that login failed (we're still on the login page).
    login_url = self.args.server_url + flask.url_for('login')
    self.assertEquals(login_url, self.driver.current_url)

    # Login as an existing admin to get access.
    LoginPage(self.driver).Login(self.args.server_url, self.args.email,
                                 self.args.password)
    self.driver.get(test_url)

    # Find the add admin dialog.
    admin_flow = AdminFlow(self.driver)
    dropdown_menu = admin_flow.getDropdownMenu()
    add_admin_dialog = admin_flow.get_add_admin_dialog(dropdown_menu)
    response_status = add_admin_dialog.find_element(
        *AdminFlow.ADD_ADMIN_RESPONSE_STATUS)
    self.assertEquals('', response_status.text)

    # Add the new admin.
    admin_flow.add_test_admin(self.TEST_ADMIN_AS_DICT['email'],
                              self.TEST_ADMIN_AS_DICT['password'],
                              add_admin_dialog)

    # Assert that it worked.
    response_status = add_admin_dialog.find_element(
        *AdminFlow.ADD_ADMIN_RESPONSE_STATUS)
    self.assertNotEqual('', response_status.text)
    admin_flow.close_dropdown_menu_from_dialog(add_admin_dialog)

    # Logout of the existing admin account.
    LoginPage(self.driver).Logout(self.args.server_url)

    # Login as the newly created test admin.
    LoginPage(self.driver).Login(self.args.server_url,
                                 self.TEST_ADMIN_AS_DICT['email'],
                                 self.TEST_ADMIN_AS_DICT['password'])
    self.driver.get(test_url)

    # Assert that login succeeded (we're now on the test_url page).
    self.assertEquals(test_url, self.driver.current_url)

  def assertAdminCanBeRemoved(self, test_url):
    """Test that removing an admin works from the given url.

    Args:
      test_url: The url to remove the admin from.
    """
    # Login as an existing admin to get access.
    LoginPage(self.driver).Login(self.args.server_url, self.args.email,
                                 self.args.password)
    self.driver.get(test_url)

    # Find the add admin dialog.
    admin_flow = AdminFlow(self.driver)
    dropdown_menu = admin_flow.getDropdownMenu()
    add_admin_dialog = admin_flow.get_add_admin_dialog(dropdown_menu)

    # Add the test admin.
    admin_flow.add_test_admin(self.TEST_ADMIN_AS_DICT['email'],
                              self.TEST_ADMIN_AS_DICT['password'],
                              add_admin_dialog)

    # Remove the test admin.
    admin_flow.close_dropdown_menu_from_dialog(add_admin_dialog)
    admin_flow.remove_test_admin(self.TEST_ADMIN_AS_DICT['email'],
                                 self.args.server_url,
                                 should_raise_exception=True,
                                 should_navigate_to_landing=False)

    # See if the admin exists.
    self.driver.get(test_url)
    dropdown_menu = admin_flow.getDropdownMenu()
    remove_admin_dialog = admin_flow.get_remove_admin_dialog(dropdown_menu)
    remove_admin_form = remove_admin_dialog.find_element(
        *AdminFlow.REMOVE_ADMIN_FORM)
    admin_item = admin_flow.find_test_admin_on_remove_form(
        self.TEST_ADMIN_AS_DICT['email'], remove_admin_form)

    self.assertIsNone(admin_item)


if __name__ == '__main__':
  unittest.main()
