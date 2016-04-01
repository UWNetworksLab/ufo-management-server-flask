"""Test base module functionality."""

import unittest

from Crypto.PublicKey import RSA
import flask
from selenium import webdriver

from landing_page import LandingPage
from layout import UfOPageLayout
from test_config import CHROME_DRIVER_LOCATION
from ufo import app

class BaseTest(unittest.TestCase):

  """Base test class to inherit from."""
  TEST_USER_AS_DICT = {
      # This name is intentionally made to be different from the server name.
      'name': 'Test User with name 01',
      'email': 'test_user@not-a-real-domain-that-should-be-in-use.com'
  }
  TEST_SERVER_AS_DICT = {
      'ip': '127.0.0.1',
      # This name is intentionally made to be different from the user name.
      'name': 'Server Fake con nombre 02',
      'private_key': 'to be filled in',
      'public_key': 'to be filled in',
  }

  def __init__(self, methodName='runTest', args=None, **kwargs):
    """Create the base test object for others to inherit."""
    super(BaseTest, self).__init__(methodName, **kwargs)
    self.args = args
    rsa_key = RSA.generate(2048)
    private_key = rsa_key.exportKey()
    public_key = rsa_key.publickey().exportKey('OpenSSH')
    BaseTest.TEST_SERVER_AS_DICT['private_key'] = private_key
    BaseTest.TEST_SERVER_AS_DICT['public_key'] = (
        public_key + ' ' + BaseTest.TEST_USER_AS_DICT['email'])

  def setUp(self):
    """Setup for test methods."""
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    # TODO(eholder) Re-enable this once we have a login module again.
    # LoginPage(self.driver).Login(self.args)

  def setContext(self):
    """Set context as test_request_context so we can use flask.url_for."""
    self.context = app.test_request_context()
    self.context.push()
    # The handlers list is added here to simplify testing against multiple
    # pages when necessary in tests that inherit from here. For example, admin
    # and settings tests need to run against multiple pages to ensure there is
    # a link present on each.
    self.handlers = [
      flask.url_for('landing'),
      flask.url_for('setup'),
      flask.url_for('search_page', search_text='"foo"')
    ]

  def tearDown(self):
    """Teardown for test methods."""
    self.driver.quit()

  def assertTestUserPresenceOnPage(self, is_present, go_to_landing=True):
    """Helper to assert whether a user is present on the landing page.

    Args:
      is_present: True for the user is present and false for not present.
      go_to_landing: True to get the landing page again (effectively a refresh
                     if the page is already on the landing) and False to use
                     whatever page the test is already on.
    """
    if go_to_landing:
      self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    test_user_item = landing_page.findTestUser(
        BaseTest.TEST_USER_AS_DICT['name'])
    if is_present:
      self.assertIsNotNone(test_user_item)
      self.assertTrue(test_user_item.is_displayed())
    else:
      self.assertIsNone(test_user_item)

  def assertTestServerPresenceOnPage(self, is_present, go_to_landing=True):
    """Helper to assert whether a server is present on the landing page.

    Args:
      is_present: True for the server is present and false for not present.
      go_to_landing: True to get the landing page again (effectively a refresh
                     if the page is already on the landing) and False to use
                     whatever page the test is already on.
    """
    if go_to_landing:
      self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    server_list = landing_page.GetElement(LandingPage.SERVER_LIST_ITEM)
    server_listbox = server_list.find_element(*LandingPage.GENERIC_LISTBOX)
    test_server_item = landing_page.findItemInListing(
        server_listbox, BaseTest.TEST_SERVER_AS_DICT['name'])
    if is_present:
      self.assertIsNotNone(test_server_item)
      self.assertTrue(test_server_item.is_displayed())
    else:
      self.assertIsNone(test_server_item)

  def assertChromePolicyDownloadLinkIsConnected(self):
    """Helper to assert that chrome policy download links to download url."""
    generic_page = UfOPageLayout(self.driver)
    download_button = generic_page.GetElement(
        UfOPageLayout.CHROME_POLICY_DOWNLOAD_BUTTON)
    actual_download_url = (
        self.args.server_url + flask.url_for('download_chrome_policy'))
    self.assertEquals(actual_download_url,
                      download_button.get_attribute('href'))

  def assertLogoLinksToLandingPage(self):
    """Helper to assert the UfO logo is an anchor to the landing page."""
    generic_page = UfOPageLayout(self.driver)
    logo_anchor = generic_page.GetElement(UfOPageLayout.LANDING_ANCHOR)
    actual_landing_url = self.args.server_url + flask.url_for('landing')
    self.assertEquals(actual_landing_url, logo_anchor.get_attribute('href'))
