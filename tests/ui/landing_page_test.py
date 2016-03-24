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
    self.removeTestUser(should_raise_exception=False)
    self.removeTestServer(should_raise_exception=False)
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

    self.assertLogoLinksToLandingPage()

    for element_by_id in LandingPage.LANDING_PAGE_ELEMENTS:
      landing_page_element = landing_page.GetElement(element_by_id)
      self.assertIsNotNone(landing_page_element)

  def testManuallyAddUserFromLandingPage(self):
    """Test that manually adding a user shows up on the user listing."""
    self.assertTestUserPresenceOnPage(False)

    self.addTestUserFromLandingPage()

    self.assertTestUserPresenceOnPage(True)

  def testDeleteUser(self):
    """Test that deleting a user removes that user."""
    self.addTestUserFromLandingPage()

    self.assertTestUserPresenceOnPage(True)

    self.removeTestUser()

    self.assertTestUserPresenceOnPage(False)

  def testAddServerFromLandingPage(self):
    """Test that adding a server shows up on the server listing."""
    self.assertTestServerPresenceOnPage(False)

    self.addTestServerFromLandingPage()

    self.assertTestServerPresenceOnPage(True)

  def testDeleteServer(self):
    """Test that deleting a server removes that server."""
    self.addTestServerFromLandingPage()

    self.assertTestServerPresenceOnPage(True)

    self.removeTestServer()

    self.assertTestServerPresenceOnPage(False)

  def testDownloadChromePolicyFromLandingPage(self):
    """Test that the chrome policy download link is present and wired up."""
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    self.assertChromePolicyDownloadLinkIsConnected()


if __name__ == '__main__':
  unittest.main()
