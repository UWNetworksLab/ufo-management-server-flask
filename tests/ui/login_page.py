"""Login page module to log a user in for testing."""

import flask
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base_driver import BaseDriver


class LoginPage(BaseDriver):

  """The UfO login page."""

  # pylint: disable=too-few-public-methods

  LOGIN_FORM = (By.ID, 'loginForm')
  USERNAME_INPUT = (By.ID, 'username')
  PASSWORD_INPUT = (By.ID, 'password')
  SIGN_IN_BUTTON = (By.ID, 'signIn')

  # If we ever need to use the Google sign-in flow, see here for an example of
  # how to do that instead of signing in directly to the management server:
  # https://github.com/uProxy/ufo-management-server/blob/master/tests/ui/login_page.py

  def _IsElementPresent(self, locator):
    """Determine if element is present."""
    try:
      self.driver.find_element(*locator)
    except NoSuchElementException:
      return False
    return True

  def Login(self, args):
    """Go through the login and authorization flows."""
    self.driver.get(args.server_url + flask.url_for('login'))

    login_form = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(((self.LOGIN_FORM))))
    username_paper_input = login_form.find_element(*self.USERNAME_INPUT)
    username_input = username_paper_input.find_element(By.ID, 'input')
    username_input.send_keys(args.username)

    password_paper_input = login_form.find_element(*self.PASSWORD_INPUT)
    password_input = password_paper_input.find_element(By.ID, 'input')
    password_input.send_keys(args.password)

    sign_in_button = self.driver.find_element(*self.SIGN_IN_BUTTON)
    sign_in_button.click()
