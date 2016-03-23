"""Test base module functionality."""

import unittest

from Crypto.PublicKey import RSA
import flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from landing_page import LandingPage
from layout import UfOPageLayout
from test_config import CHROME_DRIVER_LOCATION
from ufo import app

class BaseTest(unittest.TestCase):

  """Base test class to inherit from."""
  TEST_USER_AS_DICT = {
      'name': 'Test User Fake Name 01',
      'email': 'test_user@not-a-real-domain-that-should-be-in-use.com'
  }
  TEST_SERVER_AS_DICT = {
      'ip': '127.0.0.1',
      'name': 'Test Server Fake Name 01',
      'private_key': 'to be filled in',
      'public_key': 'to be filled in',
  }
  DEFAULT_TIMEOUT = 30

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

  def tearDown(self):
    """Teardown for test methods."""
    self.driver.quit()

  def add_test_user_helper(self):
    """Manually add a test user once the tabs are displayed."""
    add_manually_form = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((UfOPageLayout.ADD_MANUALLY_FORM))))
    name_paper_input = add_manually_form.find_element(
        *UfOPageLayout.ADD_MANUALLY_INPUT_NAME)
    name_input = name_paper_input.find_element(By.ID, 'input')
    name_input.send_keys(BaseTest.TEST_USER_AS_DICT['name'])
    email_paper_input = add_manually_form.find_element(
        *UfOPageLayout.ADD_MANUALLY_INPUT_EMAIL)
    email_input = email_paper_input.find_element(By.ID, 'input')
    email_input.send_keys(BaseTest.TEST_USER_AS_DICT['email'])
    submit_button = self.driver.find_element(
        *UfOPageLayout.ADD_MANUALLY_SUBMIT_BUTTON)
    submit_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.ADD_MANUALLY_SPINNER))))

  def remove_test_user(self, shouldRaiseException=True):
    """Manually remove a test user using the landing page (the only way).

    Args:
      shouldRaiseException: True to raise an exception if the user is not
                            found.
    """
    # Find the user and navigate to their details page.
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    user_list_item = landing_page.GetElement(LandingPage.USER_LIST_ITEM)
    user_listbox = user_list_item.find_element(*LandingPage.GENERIC_LISTBOX)
    user_item = self.find_item_in_listing(
        user_listbox, BaseTest.TEST_USER_AS_DICT['name'])

    if user_item is None:
      if shouldRaiseException:
        raise Exception
      else:
        return
    else:
      user_item.click()

    # Click delete on that user.
    details_modal = user_item.find_element(*LandingPage.DETAILS_MODAL)
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.visibility_of(details_modal))
    delete_button = details_modal.find_element(*LandingPage.USER_DELETE_BUTTON)
    delete_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            LandingPage.USER_DELETE_SPINNER))))

  def find_item_in_listing(self, listing, name):
    """Given the listing of items and a name, return the name's anchor.

    Args:
      listing: The paper-listbox element holding all items.
      name: The name of an item to search for.

    Returns:
      The anchor element for visiting the given item's details page or None.
    """
    items = listing.find_elements(By.TAG_NAME, 'paper-icon-item')
    for item in items:
      # This can technically return multiple, but it will only return one.
      div = item.find_elements(By.CLASS_NAME, 'first-div')[0]
      strong = div.find_elements(By.TAG_NAME, 'strong')[0]
      if name.lower() in strong.text.lower():
        return item
    return None

  def add_test_server_helper(self, containingElement):
    """Add a test server using the element container to find the add form.

    Args:
      containingElement: An element containing the add server form.
    """
    add_server_form = containingElement.find_element(
        *UfOPageLayout.ADD_SERVER_FORM)

    ip_paper_input = add_server_form.find_element(
        *UfOPageLayout.ADD_SERVER_INPUT_IP)
    ip_input = ip_paper_input.find_element(By.ID, 'input')
    ip_input.send_keys(BaseTest.TEST_SERVER_AS_DICT['ip'])

    name_paper_input = add_server_form.find_element(
        *UfOPageLayout.ADD_SERVER_INPUT_NAME)
    name_input = name_paper_input.find_element(By.ID, 'input')
    name_input.send_keys(BaseTest.TEST_SERVER_AS_DICT['name'])

    private_key_paper_input = add_server_form.find_element(
        *UfOPageLayout.ADD_SERVER_INPUT_PRIVATE_KEY)
    private_key_input = private_key_paper_input.find_element(By.ID, 'textarea')
    private_key_input.send_keys(BaseTest.TEST_SERVER_AS_DICT['private_key'])

    public_key_paper_input = add_server_form.find_element(
        *UfOPageLayout.ADD_SERVER_INPUT_PUBLIC_KEY)
    public_key_input = public_key_paper_input.find_element(By.ID, 'input')
    public_key_input.send_keys(BaseTest.TEST_SERVER_AS_DICT['public_key'])

    submit_button = self.driver.find_element(
        *UfOPageLayout.ADD_SERVER_SUBMIT_BUTTON)
    submit_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.ADD_SERVER_SPINNER))))

  def remove_test_server(self, shouldRaiseException=True):
    """Remove a test server using the landing page (the only way).

    Args:
      shouldRaiseException: True to raise an exception if the server is not
                            found.
    """
    # Find the server and navigate to its details page.
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    server_list = landing_page.GetElement(LandingPage.SERVER_LIST_ITEM)
    server_listbox = server_list.find_element(*LandingPage.GENERIC_LISTBOX)
    server_item = self.find_item_in_listing(
        server_listbox, BaseTest.TEST_SERVER_AS_DICT['name'])

    if server_item is None:
      if shouldRaiseException:
        raise Exception
      else:
        return
    else:
      server_item.click()

    # Click delete on that server.
    details_modal = server_item.find_element(*LandingPage.DETAILS_MODAL)
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.visibility_of(details_modal))
    delete_button = details_modal.find_element(
        *LandingPage.SERVER_DELETE_BUTTON)
    delete_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            LandingPage.SERVER_DELETE_SPINNER))))

  def assert_test_user_presence_on_landing_page(self, isPresent):
    """Helper to assert whether a user is present on the landing page.

    Args:
      isPresent: True for the user is present and false for not present.
    """
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    user_list_item = landing_page.GetElement(LandingPage.USER_LIST_ITEM)
    user_listbox = user_list_item.find_element(*LandingPage.GENERIC_LISTBOX)
    test_user_item = self.find_item_in_listing(
        user_listbox, BaseTest.TEST_USER_AS_DICT['name'])
    if isPresent:
      self.assertIsNotNone(test_user_item)
    else:
      self.assertIsNone(test_user_item)

  def assert_test_server_presence_on_landing_page(self, isPresent):
    """Helper to assert whether a server is present on the landing page.

    Args:
      isPresent: True for the server is present and false for not present.
    """
    self.driver.get(self.args.server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    server_list = landing_page.GetElement(LandingPage.SERVER_LIST_ITEM)
    server_listbox = server_list.find_element(*LandingPage.GENERIC_LISTBOX)
    test_server_item = self.find_item_in_listing(
        server_listbox, BaseTest.TEST_SERVER_AS_DICT['name'])
    if isPresent:
      self.assertIsNotNone(test_server_item)
    else:
      self.assertIsNone(test_server_item)

  def assert_chrome_policy_download_link(self):
    """Helper to assert that chrome policy download links to download url."""
    generic_page = UfOPageLayout(self.driver)
    download_button = generic_page.GetElement(
        UfOPageLayout.CHROME_POLICY_DOWNLOAD_BUTTON)
    actual_download_url = (
        self.args.server_url + flask.url_for('download_chrome_policy'))
    self.assertEquals(actual_download_url,
                      download_button.get_attribute('href'))
