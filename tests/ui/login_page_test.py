"""Test login page module functionality."""
import unittest

import flask
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base_test import BaseTest
from login_page import LoginPage


class LoginPageTest(BaseTest):

  """Test login page functionality."""

  def setUp(self):
    """Search for test methods."""
    super(LoginPageTest, self).setUp()
    super(LoginPageTest, self).setContext()
    # Only test the ones that have getters since posts won't work without a
    # form and without the xsrf token.
    self.handlers = [
      flask.url_for('landing'), # GET
      flask.url_for('admin_list'), # GET
      # flask.url_for('add_admin'), # POST
      # flask.url_for('delete_admin'), # POST
      flask.url_for('download_chrome_policy'), # GET
      flask.url_for('proxyserver_list'), # GET
      flask.url_for('proxyserver_add'), # GET or POST
      # flask.url_for('proxyserver_edit'), # POST
      # flask.url_for('proxyserver_delete'), # POST
      flask.url_for('search_page'), # GET
      flask.url_for('search'), # GET
      flask.url_for('get_settings'), # GET
      # flask.url_for('edit_settings'), #POST
      flask.url_for('user_list'), # GET
      flask.url_for('add_user'), # GET or POST
      # flask.url_for('delete_user'), # POST
      # flask.url_for('user_get_new_key_pair'), # POST
      flask.url_for('user_get_invite_code'), # GET
      # flask.url_for('user_toggle_revoked') # POST
    ]

  def tearDown(self):
    """Teardown for test methods."""
    super(LoginPageTest, self).tearDown()

  def testLoginPageLayout(self):
    """Test the login page layout contains the elements we expect.

    This should include elements inherited from the base page,
    BASE_PAGE_ELEMENTS (defined in layout.py), as well as elements specific to
    the login page, LOGIN_PAGE_ELEMENTS. Please add to each list as the UI
    is modified to ensure this test stays up to date.
    """
    self.driver.get(self.args.server_url + flask.url_for('login'))

    login_page = LoginPage(self.driver)
    for element_by_id in LoginPage.BASE_PAGE_ELEMENTS_WITHOUT_SEARCH:
      base_page_element = login_page.GetElement(element_by_id)
      self.assertIsNotNone(base_page_element)
      self.assertTrue(base_page_element.is_displayed())

    for element_by_id in LoginPage.BASE_PAGE_SEARCH_ELEMENTS:
      base_page_search_element = login_page.GetElement(element_by_id)
      self.assertIsNotNone(base_page_search_element)
      self.assertFalse(base_page_search_element.is_displayed())

    self.assertLogoLinksToLandingPage()

    for element_by_id in LoginPage.LOGIN_PAGE_ELEMENTS:
      login_page_element = login_page.GetElement(element_by_id)
      self.assertIsNotNone(login_page_element)
      self.assertTrue(login_page_element.is_displayed())

  def testNavigatingToRestrictedPageRedirectsToLogin(self):
    """Test that navigating to a restricted page redirects to login."""
    self.assertHandlersRedirectToLoginPage()

  def testLoginThenLogoutCorrectlyResetsState(self):
    """Test restricted pages redirects to login after logout."""
    # Login first with a valid user.
    LoginPage(self.driver).Login(self.args.server_url, self.args.username,
                                 self.args.password)

    # Assert that the login worked.
    landing_url = self.args.server_url + flask.url_for('landing')
    self.driver.get(landing_url)
    self.assertEquals(landing_url, self.driver.current_url)

    # Then log back out.
    LoginPage(self.driver).Logout(self.args.server_url)

    # Now test that the user is correctly redirected.
    self.assertHandlersRedirectToLoginPage()

  def assertHandlersRedirectToLoginPage(self):
    """Assert that navigating to a restricted page redirects to login."""
    login_url = self.args.server_url + flask.url_for('login')

    for handler in self.handlers:
      test_url = self.args.server_url + handler
      self.driver.get(test_url)
      WebDriverWait(self.driver, LoginPage.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((LoginPage.MAIN_TOOLBAR))))
      self.assertEquals(login_url, self.driver.current_url)


if __name__ == '__main__':
  unittest.main()
