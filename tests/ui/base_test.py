"""Test base module functionality."""

import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from layout import UfOPageLayout
from test_config import CHROME_DRIVER_LOCATION
from ufo import app

class BaseTest(unittest.TestCase):

  """Base test class to inherit from."""
  TEST_USER_AS_DICT = {
      'name': 'Test User Fake Name 01',
      'email': 'test_user@not-a-real-domain-that-should-be-in-use.com'
  }

  def __init__(self, methodName='runTest', args=None, **kwargs):
    """Create the base test object for others to inherit."""
    super(BaseTest, self).__init__(methodName, **kwargs)
    self.args = args

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
    add_manually_form = WebDriverWait(self.driver, 10).until(
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
    WebDriverWait(self.driver, 20).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.ADD_MANUALLY_SPINNER))))

  def find_user_in_listing(self, listing, name):
    """Given the listing of users and a name, return the name's anchor.

    Args:
      listing: The paper-listbox element holding all users.
      name: The name of a user to search for.

    Returns:
      The anchor element for visiting the given user's details page or None.
    """
    items = listing.find_elements(By.TAG_NAME, 'paper-icon-item')
    for item in items:
      # This can technically return multiple, but it will only return one.
      div = item.find_elements(By.CLASS_NAME, 'first-div')[0]
      strong = div.find_elements(By.TAG_NAME, 'strong')[0]
      if name.lower() in strong.text.lower():
        return item
    return None
