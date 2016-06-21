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
      self.assertTrue(base_page_element.is_displayed())

    self.assertLogoLinksToLandingPage()

    for element_by_id in LandingPage.LANDING_PAGE_ELEMENTS:
      landing_page_element = landing_page.GetElement(element_by_id)
      self.assertIsNotNone(landing_page_element)
      self.assertTrue(landing_page_element.is_displayed())

  def testManuallyAddUserFromLandingPage(self):
    """Test that manually adding a user shows up on the user listing."""
    landing_page = LandingPage(self.driver)
    self.assertTestUserPresenceOnPage(False)

    landing_page.add_test_user(BaseTest.TEST_USER_AS_DICT['name'],
                               BaseTest.TEST_USER_AS_DICT['email'],
                               self.args.server_url)

    self.assertTestUserPresenceOnPage(True)

  def testDeleteUser(self):
    """Test that deleting a user removes that user."""
    landing_page = LandingPage(self.driver)
    landing_page.add_test_user(BaseTest.TEST_USER_AS_DICT['name'],
                               BaseTest.TEST_USER_AS_DICT['email'],
                               self.args.server_url)

    self.assertTestUserPresenceOnPage(True)

    landing_page.removeTestUser(BaseTest.TEST_USER_AS_DICT['name'],
                                self.args.server_url)

    self.assertTestUserPresenceOnPage(False)

  def testDisableAndEnableUserFromListbox(self):
    """Test that disabling and enabling a user works from the listbox."""
    landing_page = LandingPage(self.driver)
    landing_page.add_test_user(BaseTest.TEST_USER_AS_DICT['name'],
                               BaseTest.TEST_USER_AS_DICT['email'],
                               self.args.server_url)
    self.assertTestUserPresenceOnPage(True)

    self.verifyUserCanBeDisabledAndThenEnabled(True, True)

  def testDisableAndEnableUserFromDetailsDialog(self):
    """Test that disabling and enabling a user works from the details page."""
    landing_page = LandingPage(self.driver)
    landing_page.add_test_user(BaseTest.TEST_USER_AS_DICT['name'],
                               BaseTest.TEST_USER_AS_DICT['email'],
                               self.args.server_url)
    self.assertTestUserPresenceOnPage(True)

    self.verifyUserCanBeDisabledAndThenEnabled(False, True)

  def testCreateNewInviteCode(self):
    """Test that creating a new invite code actually generates a new one."""
    landing_page = LandingPage(self.driver)
    # Create test user and get it.
    landing_page.add_test_user(BaseTest.TEST_USER_AS_DICT['name'],
                               BaseTest.TEST_USER_AS_DICT['email'],
                               self.args.server_url)
    self.assertTestUserPresenceOnPage(True)
    test_user_item = landing_page.findTestUser(
        BaseTest.TEST_USER_AS_DICT['name'])

    # Navigate to details dialog.
    details_dialog = landing_page.getDetailsDialogForItem(test_user_item)

    # Get the initial invite code.
    initial_invite_code = details_dialog.find_element(
        *LandingPage.USER_INVITE_CODE_TEXT).get_attribute('value')

    # Click new invite code on that user.
    get_invite_code_button = details_dialog.find_element(
        *LandingPage.USER_ROTATE_KEYS_BUTTON)
    get_invite_code_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, LandingPage.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            LandingPage.USER_DETAILS_SPINNER))))

    # Renavigate to the landing page to ensure the backend changed vs just a
    # UI update if specified.
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    test_user_item = landing_page.findTestUser(
        BaseTest.TEST_USER_AS_DICT['name'])

    # Set the container element to find the disable/enable button and text on.
    # Will be either the item within the listbox or the overall details dialog.
    details_dialog = landing_page.getDetailsDialogForItem(test_user_item)

    # Check the invite code text changed.
    final_invite_code = details_dialog.find_element(
        *LandingPage.USER_INVITE_CODE_TEXT).get_attribute('value')
    self.assertNotEquals(initial_invite_code, final_invite_code)

  def testAddServerFromLandingPage(self):
    """Test that adding a server shows up on the server listing."""
    landing_page = LandingPage(self.driver)
    self.assertTestServerPresenceOnPage(False)

    landing_page.addTestServer(BaseTest.TEST_SERVER_AS_DICT['ip'],
                               BaseTest.TEST_SERVER_AS_DICT['name'],
                               BaseTest.TEST_SERVER_AS_DICT['ssh_private_key'],
                               BaseTest.TEST_SERVER_AS_DICT['host_public_key'],
                               self.args.server_url)

    self.assertTestServerPresenceOnPage(True)

  def testDeleteServer(self):
    """Test that deleting a server removes that server."""
    landing_page = LandingPage(self.driver)
    landing_page.addTestServer(BaseTest.TEST_SERVER_AS_DICT['ip'],
                               BaseTest.TEST_SERVER_AS_DICT['name'],
                               BaseTest.TEST_SERVER_AS_DICT['ssh_private_key'],
                               BaseTest.TEST_SERVER_AS_DICT['host_public_key'],
                               self.args.server_url)

    self.assertTestServerPresenceOnPage(True)

    landing_page.removeTestServer(BaseTest.TEST_SERVER_AS_DICT['name'],
                                  self.args.server_url,
                                  should_raise_exception=False)

    self.assertTestServerPresenceOnPage(False)

  def testEditServer(self):
    """Test that editing a server displays the modified server."""
    landing_page = LandingPage(self.driver)
    landing_page.addTestServer(BaseTest.TEST_SERVER_AS_DICT['ip'],
                               BaseTest.TEST_SERVER_AS_DICT['name'],
                               BaseTest.TEST_SERVER_AS_DICT['ssh_private_key'],
                               BaseTest.TEST_SERVER_AS_DICT['host_public_key'],
                               self.args.server_url)

    self.assertTestServerPresenceOnPage(True)

    landing_page.editTestServer(
        BaseTest.TEST_SERVER_AS_DICT['name'],
        BaseTest.TEST_SERVER_EDIT_AS_DICT['ip'],
        BaseTest.TEST_SERVER_EDIT_AS_DICT['name'],
        BaseTest.TEST_SERVER_EDIT_AS_DICT['ssh_private_key'],
        BaseTest.TEST_SERVER_EDIT_AS_DICT['host_public_key'],
        self.args.server_url)

    self.assertTestServerPresenceOnPage(False)
    self.assertTestServerPresenceOnPage(
        True, name=BaseTest.TEST_SERVER_EDIT_AS_DICT['name'])

    landing_page.removeTestServer(BaseTest.TEST_SERVER_EDIT_AS_DICT['name'],
                                  self.args.server_url,
                                  should_raise_exception=False)

  def testDownloadChromePolicyFromLandingPage(self):
    """Test that the chrome policy download link is present and wired up."""
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    self.assertChromePolicyDownloadLinkIsConnected()

  def verifyUserCanBeDisabledAndThenEnabled(self, should_use_listbox,
                                            should_refresh_page):
    """Helper method for testing disabling and enabling a user.

    Args:
      should_use_listbox: If true, it will disable and enable a user from the
                          user listbox. Otherwise, it will use the details
                          dialog.
      should_refresh_page: If true, it will refresh the login page in between
                           to check that the backend updates with the UI.
    """
    landing_page = LandingPage(self.driver)
    test_user_item = landing_page.findTestUser(
        BaseTest.TEST_USER_AS_DICT['name'])

    # Set the container element to find the disable/enable button and text on.
    # Will be either the item within the listbox or the overall details dialog.
    container_element = landing_page.getContainerElementForItem(
        test_user_item, should_use_listbox)

    # Get the initial enable/disable text.
    initial_disabled_enabled_button_text = container_element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_BUTTON).text

    # Click disable on that user.
    landing_page.clickDisableEnableOnUserElement(container_element)

    # Renavigate to the landing page to ensure the backend changed vs just a
    # UI update if specified.
    if should_refresh_page:
      self.driver.get(self.args.server_url + flask.url_for('landing'))
      test_user_item = landing_page.findTestUser(
        BaseTest.TEST_USER_AS_DICT['name'])

    # Set the container element to find the disable/enable button and text on.
    # Will be either the item within the listbox or the overall details dialog.
    container_element = landing_page.getContainerElementForItem(
        test_user_item, should_use_listbox)

    # Check the enable/disable text changed.
    changed_disabled_enabled_button_text = container_element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_BUTTON).text
    self.assertNotEquals(initial_disabled_enabled_button_text,
                         changed_disabled_enabled_button_text)

    # Flip back to enable.
    landing_page.clickDisableEnableOnUserElement(container_element)

    # Renavigate to the landing page to ensure the backend changed vs just a
    # UI update if specified.
    if should_refresh_page:
      self.driver.get(self.args.server_url + flask.url_for('landing'))
      test_user_item = landing_page.findTestUser(
        BaseTest.TEST_USER_AS_DICT['name'])

    # Set the container element to find the disable/enable button and text on.
    container_element = landing_page.getContainerElementForItem(
        test_user_item, should_use_listbox)

    # Check the enable/disable text changed back to the initial.
    final_disabled_enabled_button_text = container_element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_BUTTON).text
    self.assertNotEquals(changed_disabled_enabled_button_text,
                         final_disabled_enabled_button_text)
    self.assertEquals(initial_disabled_enabled_button_text,
                      final_disabled_enabled_button_text)


if __name__ == '__main__':
  unittest.main()
