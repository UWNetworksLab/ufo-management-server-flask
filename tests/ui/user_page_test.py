"""Test user page module functionality."""
import unittest

from base_test import BaseTest
from user_page import UserPage

import flask
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class UserPageTest(BaseTest):

  """Test user page functionality."""
  TEST_USER_AS_DICT = {
      'name': 'Test User Fake Name 01',
      'email': 'test_user@not-a-real-domain-that-should-be-in-use.com'
  }

  def setUp(self):
    """Setup for test methods."""
    # TODO(eholder): Improve the checks here to be based on something more
    # robust, such as the presence of element id's or that the page renders
    # as expected, since this text can change in the future and is not i18ned.
    super(UserPageTest, self).setUp()
    super(UserPageTest, self).setContext()

  def testUserListPageRenders(self):
    """Test the user list page."""
    self.driver.get(self.args.server_url + flask.url_for('user_list'))
    user_page = UserPage(self.driver)
    add_users_link = user_page.GetLink(UserPage.ADD_USERS_LINK)
    self.assertEquals(self.args.server_url + flask.url_for('add_user'),
                      add_users_link.get_attribute('href'))
    self.assertIsNotNone(user_page.GetSidebar())
    self.assertIsNotNone(user_page.GetElement(UserPage.USER_LISTING))

  def testUserAddPageRenders(self):
    """Test the user add page."""
    self.driver.get(self.args.server_url + flask.url_for('add_user'))
    user_page = UserPage(self.driver)
    self.assertIsNotNone(user_page.GetSidebar())
    self.assertIsNotNone(user_page.GetElement(UserPage.ADD_USERS_TABS))

  def testUserAddLinksFromUserList(self):
    """Test that clicking the link from user list directs to user add."""
    self.driver.get(self.args.server_url + flask.url_for('user_list'))
    user_page = UserPage(self.driver)
    add_users_link = user_page.GetLink(UserPage.ADD_USERS_LINK)
    add_users_link.click()

    add_tabs = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(((UserPage.ADD_USERS_TABS))))
    self.assertIsNotNone(user_page.GetSidebar())
    self.assertIsNotNone(user_page.GetElement(UserPage.ADD_USERS_TABS))

  def testManualUserAdd(self):
    """Test that manually adding a user shows up on the list user page."""
    self.driver.get(self.args.server_url + flask.url_for('user_list'))
    user_page = UserPage(self.driver)
    user_listing = user_page.GetElement(UserPage.USER_LISTING)
    test_user_anchor = self._findUserInListing(
        user_listing, UserPageTest.TEST_USER_AS_DICT['email'])
    self.assertIsNone(test_user_anchor)

    self._addTestUser()

    user_listing = user_page.GetElement(UserPage.USER_LISTING)
    test_user_anchor = self._findUserInListing(
        user_listing, UserPageTest.TEST_USER_AS_DICT['email'])
    self.assertIsNotNone(test_user_anchor)

  def testUserDelete(self):
    """Test that deleting a user removes that user."""
    self.driver.get(self.args.server_url + flask.url_for('user_list'))
    user_page = UserPage(self.driver)

    self._addTestUser()

    user_listing = user_page.GetElement(UserPage.USER_LISTING)
    test_user_anchor = self._findUserInListing(
        user_listing, UserPageTest.TEST_USER_AS_DICT['email'])
    self.assertIsNotNone(test_user_anchor)

    self._removeTestUser()

    user_listing = user_page.GetElement(UserPage.USER_LISTING)
    test_user_anchor = self._findUserInListing(
        user_listing, UserPageTest.TEST_USER_AS_DICT['email'])
    self.assertIsNone(test_user_anchor)

  def _addTestUser(self):
    """Manually add a test user."""
    # Navigate to add user and go to manual tab
    self.driver.get(self.args.server_url + flask.url_for('add_user'))
    user_page = UserPage(self.driver)
    add_manually_tab = user_page.GetElement(UserPage.ADD_MANUALLY_TAB)
    add_manually_tab.click()

    # Input test name and email then submit the form
    add_manually_form = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(((UserPage.ADD_MANUALLY_FORM))))
    name_paper_input = add_manually_form.find_element(
        *UserPage.ADD_MANUALLY_INPUT_NAME)
    name_input = name_paper_input.find_element(By.ID, 'input')
    name_input.send_keys(UserPageTest.TEST_USER_AS_DICT['name'])
    email_paper_input = add_manually_form.find_element(
        *UserPage.ADD_MANUALLY_INPUT_EMAIL)
    email_input = email_paper_input.find_element(By.ID, 'input')
    email_input.send_keys(UserPageTest.TEST_USER_AS_DICT['email'])
    submit_button = add_manually_form.find_element(*UserPage.SUBMIT_BUTTON)
    submit_button.click()

    # Redirect to user listing page
    user_listing = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(((UserPage.USER_LISTING))))

  def _removeTestUser(self, raiseException=True):
    """Manually remove a test user.

    Args:
      raiseException: True to raise an exception if the user is not found.
    """
    # Find the user and navigate to their details page.
    self.driver.get(self.args.server_url + flask.url_for('user_list'))
    user_page = UserPage(self.driver)
    user_listing = user_page.GetElement(UserPage.USER_LISTING)
    anchor = self._findUserInListing(user_listing,
                                     UserPageTest.TEST_USER_AS_DICT['email'])
    if anchor is None:
      if raiseException:
        raise Exception
      else:
        return
    else:
      anchor.click()

    # Click delete on that user.
    delete_form = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(((UserPage.DELETE_FORM))))
    submit_button = delete_form.find_element(*UserPage.SUBMIT_BUTTON)
    submit_button.click()

    # Redirect to user listing page
    user_listing = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(((UserPage.USER_LISTING))))

  def _findUserInListing(self, listing, email):
    """Given the listing of users and an email, return the email's anchor.

    Args:
      listing: The paper-listbox element holding all users.
      email: The email of a user to search for.

    Returns:
      The anchor element for visiting the given user's details page or None.
    """
    anchors = listing.find_elements(By.TAG_NAME, 'a')
    for anchor in anchors:
      if email in anchor.text:
        return anchor
    return None

  def tearDown(self):
    """Teardown for test methods."""
    self._removeTestUser(raiseException=False)
    super(UserPageTest, self).tearDown()


if __name__ == '__main__':
  unittest.main()
