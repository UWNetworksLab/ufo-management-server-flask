"""Test admin flows, for now just add."""
import unittest

import flask
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base_test import BaseTest
from login_page import LoginPage
from layout import UfOPageLayout


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
    self.removeTestAdmin(should_raise_exception=False)
    LoginPage(self.driver).Logout(self.args.server_url)
    super(AdminFlowTest, self).tearDown()

  def testAddingAnotherAdminWorks(self):
    """Test that adding another admin works and lets us login as that admin."""
    # Try to login with the uncreated admin to ensure it does not exist.
    LoginPage(self.driver).Login(self.args.server_url,
                                 self.TEST_ADMIN_AS_DICT['username'],
                                 self.TEST_ADMIN_AS_DICT['password'])
    self.driver.get(self.args.server_url + flask.url_for('landing'))

    # Assert that login failed (we're still on the login page).
    login_url = self.args.server_url + flask.url_for('login')
    self.assertEquals(login_url, self.driver.current_url)

    # Login as an existing admin to get access.
    LoginPage(self.driver).Login(self.args.server_url, self.args.username,
                                 self.args.password)
    self.driver.get(self.args.server_url + flask.url_for('landing'))

    # Find the add admin dialog.
    dropdown_menu = self.getDropdownMenu()
    add_admin_dialog = self.getAddAdminDialog(dropdown_menu)
    with self.assertRaises(NoSuchElementException):
      response_status = add_admin_dialog.find_element(
          *UfOPageLayout.ADD_ADMIN_RESPONSE_STATUS)
      self.assertIsNone(response_status)

    # Add the new admin.
    self.addTestAdmin(add_admin_dialog)

    # Assert that it worked.
    response_status = add_admin_dialog.find_element(
        *UfOPageLayout.ADD_ADMIN_RESPONSE_STATUS)
    self.assertIsNotNone(response_status)

    # Logout of the existing admin account.
    LoginPage(self.driver).Logout(self.args.server_url)

    # Login as the newly created test admin.
    LoginPage(self.driver).Login(self.args.server_url,
                                 self.TEST_ADMIN_AS_DICT['username'],
                                 self.TEST_ADMIN_AS_DICT['password'])
    self.driver.get(self.args.server_url + flask.url_for('landing'))

    # Assert that login succeeded (we're now on the landing page).
    landing_url = self.args.server_url + flask.url_for('landing')
    self.assertEquals(landing_url, self.driver.current_url)

  def testRemovingAdminWorks(self):
    """Test that removing an admin works."""
    # Login as an existing admin to get access.
    LoginPage(self.driver).Login(self.args.server_url, self.args.username,
                                 self.args.password)
    self.driver.get(self.args.server_url + flask.url_for('landing'))

    # Find the add admin dialog.
    dropdown_menu = self.getDropdownMenu()
    add_admin_dialog = self.getAddAdminDialog(dropdown_menu)

    # Add the test admin.
    self.addTestAdmin(add_admin_dialog)

    # Remove the test admin.
    self.removeTestAdmin(should_raise_exception=True)

    # See if the admin exists.
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    dropdown_menu = self.getDropdownMenu()
    remove_admin_dialog = self.getRemoveAdminDialog(dropdown_menu)
    remove_admin_form = remove_admin_dialog.find_element(
        *UfOPageLayout.REMOVE_ADMIN_FORM)
    admin_item = self.findTestAdminOnRemoveForm(remove_admin_form)

    self.assertIsNone(admin_item)

  def testAdminUsernameDisplayed(self):
    """Test that the admin's username is displayed while logged in."""
    LoginPage(self.driver).Login(self.args.server_url, self.args.username,
                                 self.args.password)
    self.driver.get(self.args.server_url + flask.url_for('landing'))

    dropdown_button = self.driver.find_element(*UfOPageLayout.OPEN_MENU_BUTTON)
    self.assertEquals(dropdown_button.text.lower(), self.args.username.lower())

  def getAddAdminDialog(self, dropdown_menu):
    """Navigates to the add admin dialog on a given page.

    Args:
      dropdown_menu: The dropdown menu to navigate upon.

    Returns:
      The add admin dialog element once found.
    """
    add_admin_button = dropdown_menu.find_element(
        *UfOPageLayout.ADD_ADMIN_BUTTON)
    add_admin_button.click()

    add_admin_dialog = WebDriverWait(
        self.driver, BaseTest.DEFAULT_TIMEOUT).until(
            EC.visibility_of_element_located(((
                UfOPageLayout.ADD_ADMIN_DIALOG))))
    return add_admin_dialog

  def getRemoveAdminDialog(self, dropdown_menu):
    """Navigates to the remove admin dialog on a given page.

    Args:
      dropdown_menu: The dropdown menu to navigate upon.

    Returns:
      The remove admin dialog element once found.
    """
    remove_admin_button = dropdown_menu.find_element(
        *UfOPageLayout.REMOVE_ADMIN_BUTTON)
    remove_admin_button.click()

    remove_admin_dialog = WebDriverWait(
        self.driver, BaseTest.DEFAULT_TIMEOUT).until(
            EC.visibility_of_element_located(((
                UfOPageLayout.REMOVE_ADMIN_DIALOG))))
    return remove_admin_dialog

  def findTestAdminOnRemoveForm(self, remove_admin_form):
    """Find and return the test admin element on the remove admin form.

    Args:
      remove_admin_form: The remove admin form to search through.

    Returns:
      The test admin element once found.
    """
    menu = remove_admin_form.find_element(By.TAG_NAME, 'paper-menu')
    return self.findItemInListing(menu, self.TEST_ADMIN_AS_DICT['username'],
                                  is_icon_item=False)

  def addTestAdmin(self, add_admin_dialog):
    """Add a test admin account using the add admin form.

    Args:
      add_admin_dialog: The add admin dialog element to find the add form on.
    """
    add_admin_form = add_admin_dialog.find_element(
        *UfOPageLayout.ADD_ADMIN_FORM)
    username_paper_input = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_USERNAME)
    username_input = username_paper_input.find_element(By.ID, 'input')
    username_input.send_keys(self.TEST_ADMIN_AS_DICT['username'])

    password_paper_input = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_PASSWORD)
    password_input = password_paper_input.find_element(By.ID, 'input')
    password_input.send_keys(self.TEST_ADMIN_AS_DICT['password'])

    submit_button = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_SUBMIT)
    submit_button.click()

    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.DROPDOWN_MENU_SPINNER))))

  def removeTestAdmin(self, should_raise_exception=True):
    """Remove a test admin account using a form post (the only way currently).

    Args:
      should_raise_exception: True to raise an exception if the admin is not
                              found.
    """
    # Find the user and navigate to their details page.
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    dropdown_menu = self.getDropdownMenu()
    remove_admin_dialog = self.getRemoveAdminDialog(dropdown_menu)
    remove_admin_form = remove_admin_dialog.find_element(
        *UfOPageLayout.REMOVE_ADMIN_FORM)
    admin_item = self.findTestAdminOnRemoveForm(remove_admin_form)

    if admin_item is None:
      if should_raise_exception:
        raise Exception
      else:
        return
    else:
      admin_item.click()

    # Click the delete button with that admin selected.
    submit_button = remove_admin_dialog.find_element(
        *UfOPageLayout.REMOVE_ADMIN_SUBMIT)
    submit_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.DROPDOWN_MENU_SPINNER))))


if __name__ == '__main__':
  unittest.main()
