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
    self._remove_test_user_from_landing_page(raiseException=False)
    LoginPage(self.driver).Logout(self.args)
    super(LandingPageTest, self).tearDown()

  # def testLandingPage(self):
  #   """Test the landing page."""
    # TODO(eholder): Improve the checks here to be based on something more
    # robust, such as the presence of element id's or that the page renders
    # as expected, since this text can change in the future and is not i18ned.
    # title = u'Uproxy for Organizations Management Server'
    # instruction = ('Click one of the links on the side to login and '
    #                'administer the server.')

    # self.driver.get(self.args.server_url + flask.url_for('landing'))

    # landing_page = LandingPage(self.driver)
    # title_elem = landing_page.GetElement(landing_page.TITLE)
    # instruction_elem = landing_page.GetElement(landing_page.INSTRUCTION)
    # self.assertEquals(title, title_elem.text)
    # self.assertEquals(instruction, instruction_elem.text)
    # self.assertIsNotNone(landing_page.GetSidebar())

  def testManualUserAdd(self):
    """Test that manually adding a user shows up on the user listing."""
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    user_list_item = landing_page.GetElement(LandingPage.USER_LIST_ITEM)
    user_listbox = user_list_item.find_element(*LandingPage.USER_LISTBOX)
    test_user_item = self.find_user_in_listing(
        user_listbox, LandingPageTest.TEST_USER_AS_DICT['name'])
    self.assertIsNone(test_user_item)

    self._add_test_user_from_landing_page()

    user_list_item = landing_page.GetElement(LandingPage.USER_LIST_ITEM)
    user_listbox = user_list_item.find_element(*LandingPage.USER_LISTBOX)
    test_user_item = self.find_user_in_listing(
        user_listbox, LandingPageTest.TEST_USER_AS_DICT['name'])
    self.assertIsNotNone(test_user_item)

  def _add_test_user_from_landing_page(self):
    """Manually add a test user using the landing page."""
    # Navigate to add user and go to manual tab
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    add_user_button = landing_page.GetElement(LandingPage.ADD_USER_BUTTON)
    add_user_button.click()
    add_manually_tab = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(((LandingPage.ADD_MANUALLY_TAB))))
    add_manually_tab.click()

    self.add_test_user_helper()

  def _remove_test_user_from_landing_page(self, raiseException=True):
    """Manually remove a test user using the landing page.

    Args:
      raiseException: True to raise an exception if the user is not found.
    """
    # Find the user and navigate to their details page.
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    user_list_item = landing_page.GetElement(LandingPage.USER_LIST_ITEM)
    user_listbox = user_list_item.find_element(*LandingPage.USER_LISTBOX)
    user_item = self.find_user_in_listing(
        user_listbox, LandingPageTest.TEST_USER_AS_DICT['name'])

    if user_item is None:
      if raiseException:
        raise Exception
      else:
        return
    else:
      user_item.click()

    # Click delete on that user.
    details_modal = user_item.find_element(*LandingPage.USER_DETAILS_MODAL)
    WebDriverWait(self.driver, 10).until(
        EC.visibility_of(details_modal))
    delete_button = details_modal.find_element(*LandingPage.USER_DELETE_BUTTON)
    delete_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, 20).until(
        EC.invisibility_of_element_located(((
            LandingPage.USER_DELETE_SPINNER))))


if __name__ == '__main__':
  unittest.main()
