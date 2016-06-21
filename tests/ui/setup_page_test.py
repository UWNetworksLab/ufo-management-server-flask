"""Test setup page module functionality."""
import unittest

import flask

from base_test import BaseTest
from landing_page import LandingPage
from login_page import LoginPage
from setup_page import SetupPage
from settings_component import SettingsComponent


class SetupPageTest(BaseTest):

  """Test setup page functionality."""

  def setUp(self):
    """Setup for test methods."""
    super(SetupPageTest, self).setUp()
    super(SetupPageTest, self).setContext()
    LoginPage(self.driver).Login(self.args.server_url, self.args.email,
                                 self.args.password)

  def tearDown(self):
    """Teardown for test methods."""
    landing_page = LandingPage(self.driver)
    landing_page.removeTestUser(BaseTest.TEST_USER_AS_DICT['name'],
                                self.args.server_url,
                                should_raise_exception=False)
    landing_page.removeTestServer(BaseTest.TEST_SERVER_AS_DICT['name'],
                                  self.args.server_url,
                                  should_raise_exception=False)
    LoginPage(self.driver).Logout(self.args.server_url)
    super(SetupPageTest, self).tearDown()

  def testSetupPageLayout(self):
    """Test the setup page layout contains the elements we expect.

    This should include elements inherited from the base page,
    BASE_PAGE_ELEMENTS (defined in layout.py), as well as elements specific to
    the setup page, SETUP_PAGE_ELEMENTS. Please add to each list as the UI
    is modified to ensure this test stays up to date.
    """
    self.driver.get(self.args.server_url + flask.url_for('setup'))

    setup_page = SetupPage(self.driver)
    for element_by_id in SetupPage.BASE_PAGE_ELEMENTS:
      base_page_element = setup_page.GetElement(element_by_id)
      self.assertIsNotNone(base_page_element)
      self.assertTrue(base_page_element.is_displayed())

    self.assertLogoLinksToLandingPage()

    for element_by_id in SetupPage.SETUP_PAGE_ELEMENTS:
      setup_page_element = setup_page.GetElement(element_by_id)
      self.assertIsNotNone(setup_page_element)
      self.assertTrue(setup_page_element.is_displayed())

  def testManuallyAddUserFromSetupPage(self):
    """Test that manually adding a user shows up on the user listing."""
    setup_page = SetupPage(self.driver)
    self.assertTestUserPresenceOnPage(False)

    setup_page.addTestUser(BaseTest.TEST_USER_AS_DICT['name'],
                           BaseTest.TEST_USER_AS_DICT['email'],
                           self.args.server_url)

    self.assertTestUserPresenceOnPage(True)

  def testAddServerFromSetupPage(self):
    """Test that adding a server shows up on the server listing."""
    setup_page = SetupPage(self.driver)
    self.assertTestServerPresenceOnPage(False)

    setup_page.addTestServer(BaseTest.TEST_SERVER_AS_DICT['ip'],
                             BaseTest.TEST_SERVER_AS_DICT['name'],
                             BaseTest.TEST_SERVER_AS_DICT['ssh_private_key'],
                             BaseTest.TEST_SERVER_AS_DICT['host_public_key'],
                             self.args.server_url)

    self.assertTestServerPresenceOnPage(True)

  def testDownloadChromePolicyFromSetupPage(self):
    """Test that the chrome policy download link is present and wired up."""
    self.driver.get(self.args.server_url + flask.url_for('setup'))
    self.assertChromePolicyDownloadLinkIsConnected()


if __name__ == '__main__':
  unittest.main()
