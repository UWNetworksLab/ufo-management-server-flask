"""Test langing page module functionality."""
import unittest

import flask
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
    self.removeTestUser(shouldRaiseException=False)
    self.removeTestServer(shouldRaiseException=False)
    LoginPage(self.driver).Logout(self.args)
    super(LandingPageTest, self).tearDown()

  def testLandingPageLayout(self):
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

  def testManuallyAddUserFromLandingPage(self):
    """Test that manually adding a user shows up on the user listing."""
    self.assertTestUserPresenceOnLandingPage(False)

    self._addTestUserFromLandingPage()

    self.assertTestUserPresenceOnLandingPage(True)

  def testDeleteUser(self):
    """Test that deleting a user removes that user."""
    self._addTestUserFromLandingPage()

    self.assertTestUserPresenceOnLandingPage(True)

    self.removeTestUser()

    self.assertTestUserPresenceOnLandingPage(False)

  def testAddServerFromLandingPage(self):
    """Test that adding a server shows up on the server listing."""
    self.assertTestServerPresenceOnLandingPage(False)

    self._addTestServerFromLandingPage()

    self.assertTestServerPresenceOnLandingPage(True)

  def testDeleteServer(self):
    """Test that deleting a server removes that server."""
    self._addTestServerFromLandingPage()

    self.assertTestServerPresenceOnLandingPage(True)

    self.removeTestServer()

    self.assertTestServerPresenceOnLandingPage(False)

  def testDownloadChromePolicyFromLandingPage(self):
    """Test that the chrome policy download link is present and wired up."""
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    self.assertChromePolicyDownloadLinkIsConnected()

  def _addTestUserFromLandingPage(self):
    """Manually add a test user using the landing page."""
    # Navigate to add user and go to manual tab.
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    add_user_button = landing_page.GetElement(LandingPage.ADD_USER_BUTTON)
    add_user_button.click()
    add_manually_tab = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((LandingPage.ADD_MANUALLY_TAB))))
    add_manually_tab.click()

    self.addTestUserHelper()

  def _addTestServerFromLandingPage(self):
    """Add a test server using the landing page."""
    # Navigate to add server.
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    add_server_button = landing_page.GetElement(LandingPage.ADD_SERVER_BUTTON)
    add_server_button.click()
    add_server_modal = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((LandingPage.ADD_SERVER_MODAL))))

    self.addTestServerHelper(add_server_modal)


if __name__ == '__main__':
  unittest.main()
