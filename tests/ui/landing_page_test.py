"""Test langing page module functionality."""
import unittest

import flask
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base_test import BaseTest
from landing_page import LandingPage
from login_page import LoginPage


class LandingPageTest(BaseTest):

  """Test landing page functionality."""

  def setUp(self):
    """Setup for test methods."""
    super(LandingPageTest, self).setUp()
    super(LandingPageTest, self).setContext()
    LoginPage(self.driver).Login(self.args)

  def tearDown(self):
    """Teardown for test methods."""
    self.remove_test_user(raiseException=False)
    self.remove_test_server(raiseException=False)
    LoginPage(self.driver).Logout(self.args)
    super(LandingPageTest, self).tearDown()

  def testLandingPage(self):
    """Test the landing page layout contains the elements we expect.

    This should include elements inherited from the base page,
    BASE_PAGE_ELEMENTS (defined in layout.py), as well as elements specific to
    the landing page, LANDING_PAGE_ELEMENTS. Please add to each list as the UI
    is modified to ensure this test stays up to date.
    """
    self.driver.get(self.args.server_url + flask.url_for('landing'))

    landing_page = LandingPage(self.driver)
    for element_by_id in LandingPage.BASE_PAGE_ELEMENTS:
      base_page_element = landing_page.GetElement(element_by_id)
      self.assertIsNotNone(base_page_element)

    for element_by_id in LandingPage.LANDING_PAGE_ELEMENTS:
      landing_page_element = landing_page.GetElement(element_by_id)
      self.assertIsNotNone(landing_page_element)

  def testManualUserAdd(self):
    """Test that manually adding a user shows up on the user listing."""
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    user_list_item = landing_page.GetElement(LandingPage.USER_LIST_ITEM)
    user_listbox = user_list_item.find_element(*LandingPage.GENERIC_LISTBOX)
    test_user_item = self.find_item_in_listing(
        user_listbox, LandingPageTest.TEST_USER_AS_DICT['name'])
    self.assertIsNone(test_user_item)

    self._add_test_user_from_landing_page()

    user_list_item = landing_page.GetElement(LandingPage.USER_LIST_ITEM)
    user_listbox = user_list_item.find_element(*LandingPage.GENERIC_LISTBOX)
    test_user_item = self.find_item_in_listing(
        user_listbox, LandingPageTest.TEST_USER_AS_DICT['name'])
    self.assertIsNotNone(test_user_item)

  def testUserDelete(self):
    """Test that deleting a user removes that user."""
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)

    self._add_test_user_from_landing_page()

    user_list_item = landing_page.GetElement(LandingPage.USER_LIST_ITEM)
    user_listbox = user_list_item.find_element(*LandingPage.GENERIC_LISTBOX)
    test_user_item = self.find_item_in_listing(
        user_listbox, LandingPageTest.TEST_USER_AS_DICT['name'])
    self.assertIsNotNone(test_user_item)

    self.remove_test_user()

    user_list_item = landing_page.GetElement(LandingPage.USER_LIST_ITEM)
    user_listbox = user_list_item.find_element(*LandingPage.GENERIC_LISTBOX)
    test_user_item = self.find_item_in_listing(
        user_listbox, LandingPageTest.TEST_USER_AS_DICT['name'])
    self.assertIsNone(test_user_item)

  def testServerAdd(self):
    """Test that adding a server shows up on the server listing."""
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    server_list = landing_page.GetElement(LandingPage.SERVER_LIST_ITEM)
    server_listbox = server_list.find_element(*LandingPage.GENERIC_LISTBOX)
    test_server_item = self.find_item_in_listing(
        server_listbox, LandingPageTest.TEST_SERVER_AS_DICT['name'])
    self.assertIsNone(test_server_item)

    self._add_test_server_from_landing_page()

    server_list = landing_page.GetElement(LandingPage.SERVER_LIST_ITEM)
    server_listbox = server_list.find_element(*LandingPage.GENERIC_LISTBOX)
    test_server_item = self.find_item_in_listing(
        server_listbox, LandingPageTest.TEST_SERVER_AS_DICT['name'])
    self.assertIsNotNone(test_server_item)

  def testServerDelete(self):
    """Test that deleting a server removes that server."""
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)

    self._add_test_server_from_landing_page()

    server_list = landing_page.GetElement(LandingPage.SERVER_LIST_ITEM)
    server_listbox = server_list.find_element(*LandingPage.GENERIC_LISTBOX)
    test_server_item = self.find_item_in_listing(
        server_listbox, LandingPageTest.TEST_SERVER_AS_DICT['name'])
    self.assertIsNotNone(test_server_item)

    self.remove_test_server()

    server_list = landing_page.GetElement(LandingPage.SERVER_LIST_ITEM)
    server_listbox = server_list.find_element(*LandingPage.GENERIC_LISTBOX)
    test_server_item = self.find_item_in_listing(
        server_listbox, LandingPageTest.TEST_SERVER_AS_DICT['name'])
    self.assertIsNone(test_server_item)

  def _add_test_user_from_landing_page(self):
    """Manually add a test user using the landing page."""
    # Navigate to add user and go to manual tab.
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    add_user_button = landing_page.GetElement(LandingPage.ADD_USER_BUTTON)
    add_user_button.click()
    add_manually_tab = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(((LandingPage.ADD_MANUALLY_TAB))))
    add_manually_tab.click()

    self.add_test_user_helper()

  def _add_test_server_from_landing_page(self):
    """Add a test server using the landing page."""
    # Navigate to add server.
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    add_server_button = landing_page.GetElement(LandingPage.ADD_SERVER_BUTTON)
    add_server_button.click()

    self.add_test_server_helper()


if __name__ == '__main__':
  unittest.main()
