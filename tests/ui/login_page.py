"""Login page module to log a user in for testing."""

import flask
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from layout import UfOPageLayout


class LoginPage(UfOPageLayout):

  """The UfO login page."""

  # pylint: disable=too-few-public-methods

  LOGIN_FORM = (By.ID, 'loginForm')
  EMAIL_INPUT = (By.ID, 'email')
  PASSWORD_INPUT = (By.ID, 'password')
  SIGN_IN_BUTTON = (By.ID, 'signIn')
  LOGIN_PAGE_ELEMENTS = [
    LOGIN_FORM,
    EMAIL_INPUT,
    PASSWORD_INPUT,
    SIGN_IN_BUTTON
  ]

  LOGOUT_FORM = (By.ID, 'logoutForm')
  GENERIC_PAPER_BUTTON = (By.TAG_NAME, 'paper-button')

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

  def Login(self, server_url, email, password):
    """Go through the login and authorization flows.

    Args:
      server_url: The base url for the server, such as http://0.0.0.0:5000.
      email: The email to supply for login.
      password: The password to supply for login.
    """
    self.driver.get(server_url + flask.url_for('login'))

    login_form = WebDriverWait(self.driver,
                               UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((self.LOGIN_FORM))))
    email_paper_input = login_form.find_element(*self.EMAIL_INPUT)
    email_input = email_paper_input.find_element(By.ID, 'input')
    email_input.send_keys(email)

    password_paper_input = login_form.find_element(*self.PASSWORD_INPUT)
    password_input = password_paper_input.find_element(By.ID, 'input')
    password_input.send_keys(password)

    sign_in_button = self.driver.find_element(*self.SIGN_IN_BUTTON)
    sign_in_button.click()

    # Wait for redirect to landing page.
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((LoginPage.OPEN_MENU_BUTTON))))

  def Logout(self, server_url):
    """Click through the logout flow.

    Args:
      server_url: The base url for the server, such as http://0.0.0.0:5000.
    """
    self.driver.get(server_url + flask.url_for('landing'))
    login_url = server_url + flask.url_for('login')
    if login_url == self.driver.current_url:
      # We were already logged out so don't need to do anything.
      return
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((LoginPage.OPEN_MENU_BUTTON))))
    dropdown_button = self.driver.find_element(*LoginPage.OPEN_MENU_BUTTON)
    dropdown_button.click()

    logout_form = WebDriverWait(self.driver,
                                UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((self.LOGOUT_FORM))))
    logout_button = logout_form.find_element(*self.GENERIC_PAPER_BUTTON)
    logout_button.click()

    # Wait for redirect back to login
    login_form = WebDriverWait(self.driver,
                               UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((self.LOGIN_FORM))))
