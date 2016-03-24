"""Test langing page module functionality."""
import unittest

import flask
from selenium.webdriver.common.action_chains import ActionChains
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

  def testDisableAndEnableUserFromListbox(self):
    """Test that disabling and enabling a user works from the listbox."""
    self.addTestUserFromLandingPage()
    self.assertTestUserPresenceOnPage(True)

    self.enableDisableTestHelper(True, True)

  def testDisableAndEnableUserFromDetailsDialog(self):
    """Test that disabling and enabling a user works from the details page."""
    self.addTestUserFromLandingPage()
    self.assertTestUserPresenceOnPage(True)

    self.enableDisableTestHelper(False, True)

  def testCreateNewInviteCode(self):
    """Test that creating a new invite code actually generates a new one."""
    # Create test user and get it.
    self.addTestUserFromLandingPage()
    self.assertTestUserPresenceOnPage(True)
    test_user_item = self.findTestUserOnLangingPage()

    # Navigate to details dialog.
    details_dialog = self.getDetailsDialogForItem(test_user_item)

    # Get the initial invite code.
    initial_invite_code = details_dialog.find_element(
        *LandingPage.USER_INVITE_CODE_TEXT).get_attribute('value')

    # Click new invite code on that user.
    get_invite_code_button = details_dialog.find_element(
        *LandingPage.USER_ROTATE_KEYS_BUTTON)
    get_invite_code_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            LandingPage.USER_DETAILS_SPINNER))))

    # Renavigate to the landing page to ensure the backend changed vs just a
    # UI update if specified.
    # if should_refresh_page:
    #   self.driver.get(self.args.server_url + flask.url_for('landing'))
    #   test_user_item = self.findTestUserOnLangingPage()
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    test_user_item = self.findTestUserOnLangingPage()

    # Set the container element to find the disable/enable button and text on.
    # Will be either the item within the listbox or the overall details dialog.
    details_dialog = self.getDetailsDialogForItem(test_user_item)

    # Check the invite code text changed.
    final_invite_code = details_dialog.find_element(
        *LandingPage.USER_INVITE_CODE_TEXT).get_attribute('value')
    self.assertNotEquals(initial_invite_code, final_invite_code)

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

  def enableDisableTestHelper(self, should_use_listbox, should_refresh_page):
    """Helper method for testing disabling and enabling a user.

    Args:
      should_use_listbox: If true, it will disable and enable a user from the
                          user listbox. Otherwise, it will use the details
                          dialog.
      should_refresh_page: If true, it will refresh the login page in between
                           to check that the backend updates with the UI.
    """
    test_user_item = self.findTestUserOnLangingPage()

    # Set the container element to find the disable/enable button and text on.
    # Will be either the item within the listbox or the overall details dialog.
    container_element = self.getContainerElementForItem(test_user_item,
                                                        should_use_listbox)

    # Get the initial enable/disable text.
    initial_disabled_enabled_text = container_element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_TEXT).text
    initial_disabled_enabled_button_text = container_element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_BUTTON).text

    # Click disable on that user.
    self.clickDisableEnableOnUserElement(container_element)

    # Renavigate to the landing page to ensure the backend changed vs just a
    # UI update if specified.
    if should_refresh_page:
      self.driver.get(self.args.server_url + flask.url_for('landing'))
      test_user_item = self.findTestUserOnLangingPage()

    # Set the container element to find the disable/enable button and text on.
    # Will be either the item within the listbox or the overall details dialog.
    container_element = self.getContainerElementForItem(test_user_item,
                                                        should_use_listbox)

    # Check the enable/disable text changed.
    changed_disabled_enabled_text = container_element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_TEXT).text
    changed_disabled_enabled_button_text = container_element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_BUTTON).text
    self.assertNotEquals(initial_disabled_enabled_text,
                         changed_disabled_enabled_text)
    self.assertNotEquals(initial_disabled_enabled_button_text,
                         changed_disabled_enabled_button_text)

    # Flip back to enable.
    self.clickDisableEnableOnUserElement(container_element)

    # Renavigate to the landing page to ensure the backend changed vs just a
    # UI update if specified.
    if should_refresh_page:
      self.driver.get(self.args.server_url + flask.url_for('landing'))
      test_user_item = self.findTestUserOnLangingPage()

    # Set the container element to find the disable/enable button and text on.
    container_element = self.getContainerElementForItem(test_user_item,
                                                        should_use_listbox)

    # Check the enable/disable text changed back to the initial.
    final_disabled_enabled_text = container_element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_TEXT).text
    final_disabled_enabled_button_text = container_element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_BUTTON).text
    self.assertNotEquals(changed_disabled_enabled_text,
                         final_disabled_enabled_text)
    self.assertNotEquals(changed_disabled_enabled_button_text,
                         final_disabled_enabled_button_text)
    self.assertEquals(initial_disabled_enabled_text,
                      final_disabled_enabled_text)
    self.assertEquals(initial_disabled_enabled_button_text,
                      final_disabled_enabled_button_text)

  def getContainerElementForItem(self, item, should_use_listbox):
    """Given an item, get the container element for it based on the boolean.

    I realize this method is very basic, but it is just to avoid a lot of
    duplication across some tests.

    Args:
      item: The item whose container needs to be returned.
      should_use_listbox: If true, this will just return the item itself.
                          Otherwise, this will open and return the details
                          dialog.

    Returns:
      The container for the given element based on should_use_listbox, either
      the item itself or its details dialog once opened.
    """
    if should_use_listbox:
      # Hover the item so the button shows up.
      ActionChains(self.driver).move_to_element(item).perform()
      return item
    else:
      return self.getDetailsDialogForItem(item)

  def getDetailsDialogForItem(self, item):
    """Given an item, open it's details dialog and return that element.

    Args:
      item: The item whose details dialog needs to be opened.

    Returns:
      The details dialog for the given element, once opened.
    """
    item.click()
    details_modal = item.find_element(*LandingPage.DETAILS_MODAL)
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.visibility_of(details_modal))
    return details_modal

  def clickDisableEnableOnUserElement(self, element):
    """Given a user element, click the disable/enable button on it.

    Args:
      element: The user element to click disable/enable upon.
    """
    disable_enable_button = element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_BUTTON)
    disable_enable_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            LandingPage.USER_DETAILS_SPINNER))))


if __name__ == '__main__':
  unittest.main()
