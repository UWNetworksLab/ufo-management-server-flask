"""Test base module functionality."""

import unittest

from Crypto.PublicKey import RSA
import flask
from selenium import webdriver
from selenium.webdriver.chrome import options
from selenium.webdriver.common import desired_capabilities

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
      'ssh_private_key': 'to be filled in',
      'host_public_key': 'to be filled in',
  }
  TEST_SERVER_EDIT_AS_DICT = {
      'ip': '127.0.0.127',
      # This name is intentionally made to be different from the user name.
      'name': 'Editted Machine Name',
      'ssh_private_key': 'to be filled in',
      'host_public_key': 'to be filled in',
  }

  def __init__(self, methodName='runTest', args=None, **kwargs):
    """Create the base test object for others to inherit."""
    super(BaseTest, self).__init__(methodName, **kwargs)
    self.args = args
    rsa_key = RSA.generate(2048)
    ssh_private_key = rsa_key.exportKey()
    host_public_key = rsa_key.publickey().exportKey('OpenSSH')
    BaseTest.TEST_SERVER_AS_DICT['ssh_private_key'] = ssh_private_key
    BaseTest.TEST_SERVER_AS_DICT['host_public_key'] = host_public_key

    rsa_key = RSA.generate(2048)
    ssh_private_key_edit = rsa_key.exportKey()
    host_public_key_edit = rsa_key.publickey().exportKey('OpenSSH')
    BaseTest.TEST_SERVER_EDIT_AS_DICT['ssh_private_key'] = ssh_private_key_edit
    BaseTest.TEST_SERVER_EDIT_AS_DICT['host_public_key'] = host_public_key_edit

  def setUp(self):
    """Setup for test methods."""
    custom_options = options.Options()
    custom_options.add_argument('--no-sandbox')
    capabilities = desired_capabilities.DesiredCapabilities.CHROME.copy()
    remote_variables_found = (
        self.args.sauce_username is not None and
        self.args.sauce_access_key is not None and
        self.args.travis_job_number is not None)
    if remote_variables_found:
      capabilities['browserName'] = 'chrome'
      capabilities['platform'] = 'OS X 10.10'
      capabilities['version'] = '48.0'
      capabilities['screenResolution'] = '1920x1080'
      capabilities['tunnel-identifier'] = self.args.travis_job_number
      hub_url = '%s:%s@localhost:4445' % (self.args.sauce_username,
                                          self.args.sauce_access_key)
      self.driver = webdriver.Remote(
          desired_capabilities=capabilities,
          command_executor='http://%s/wd/hub' % hub_url)
    else:
      self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION,
                                     chrome_options=custom_options)

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

  def assertTestServerPresenceOnPage(
      self, is_present, go_to_landing=True,
      name=TEST_SERVER_AS_DICT['name']):
    """Helper to assert whether a server is present on the landing page.

    Args:
      is_present: True for the server is present and false for not present.
      go_to_landing: True to get the landing page again (effectively a refresh
                     if the page is already on the landing) and False to use
                     whatever page the test is already on.
      name: The name of the server to assert upon, which defaults to the test
            server.
    """
    if go_to_landing:
      self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    server_list = landing_page.GetElement(LandingPage.SERVER_LIST_ITEM)
    server_listbox = server_list.find_element(*LandingPage.GENERIC_LISTBOX)
    test_server_item = landing_page.findItemInListing(server_listbox, name)
    if is_present:
      self.assertIsNotNone(test_server_item)
      self.assertTrue(test_server_item.is_displayed())
    else:
      self.assertIsNone(test_server_item)

  def assertChromePolicyDownloadLinkIsConnected(self):
    """Helper to assert that chrome policy download links to download url."""
    generic_page = UfOPageLayout(self.driver)
    download_button = generic_page.GetElement(
        UfOPageLayout.CHROME_POLICY_HIDDEN_BUTTON)
    prefix = 'data:text/json,'
    self.assertTrue(download_button.get_attribute('href').startswith(prefix))

  def assertLogoLinksToLandingPage(self):
    """Helper to assert the UfO logo is an anchor to the landing page."""
    generic_page = UfOPageLayout(self.driver)
    logo_anchor = generic_page.GetElement(UfOPageLayout.LANDING_ANCHOR)
    actual_landing_url = self.args.server_url + flask.url_for('landing')
    self.assertEquals(actual_landing_url, logo_anchor.get_attribute('href'))
