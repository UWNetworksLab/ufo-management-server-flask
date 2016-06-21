"""Test search page module functionality."""
import unittest

import flask

from base_test import BaseTest
from landing_page import LandingPage
from login_page import LoginPage
from search_page import SearchPage
from setup_page import SetupPage


class SearchPageTest(BaseTest):

  """Test search page functionality."""

  def setUp(self):
    """Search for test methods."""
    super(SearchPageTest, self).setUp()
    super(SearchPageTest, self).set_context()
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
    super(SearchPageTest, self).tearDown()

  def testSearchPageLayout(self):
    """Test the search page layout contains the elements we expect.

    This should include elements inherited from the base page,
    BASE_PAGE_ELEMENTS (defined in layout.py), as well as elements specific to
    the search page, SEARCH_PAGE_ELEMENTS. Please add to each list as the UI
    is modified to ensure this test stays up to date.
    """
    search_page = SearchPage(self.driver)
    search_page.searchForTestItem('foo')

    for element_by_id in SearchPage.BASE_PAGE_ELEMENTS:
      base_page_element = search_page.get_element(element_by_id)
      self.assertIsNotNone(base_page_element)
      self.assertTrue(base_page_element.is_displayed())

    self.assertLogoLinksToLandingPage()

    for element_by_id in SearchPage.SEARCH_PAGE_ELEMENTS:
      search_page_element = search_page.get_element(element_by_id)
      self.assertIsNotNone(search_page_element)
      self.assertTrue(search_page_element.is_displayed())

  def testSearchUserFromLandingPage(self):
    """Test that search displays user results within the landing page."""
    landing_page = LandingPage(self.driver)
    landing_page.addTestUser(BaseTest.TEST_USER_AS_DICT['name'],
                             BaseTest.TEST_USER_AS_DICT['email'],
                             self.args.server_url)
    self.assertTestUserPresenceOnPage(True)

    landing_page.searchForTestItem(BaseTest.TEST_USER_AS_DICT['name'])

    self.assertTestUserPresenceOnPage(True, False)
    landing_url = self.args.server_url + flask.url_for('landing')
    self.assertEquals(landing_url, self.driver.current_url)

  def testSearchServerFromLandingPage(self):
    """Test that search displays server results within the landing page."""
    landing_page = LandingPage(self.driver)
    landing_page.addTestServer(BaseTest.TEST_SERVER_AS_DICT['ip'],
                               BaseTest.TEST_SERVER_AS_DICT['name'],
                               BaseTest.TEST_SERVER_AS_DICT['ssh_private_key'],
                               BaseTest.TEST_SERVER_AS_DICT['host_public_key'],
                               self.args.server_url)
    self.assertTestServerPresenceOnPage(True)

    landing_page.searchForTestItem(BaseTest.TEST_SERVER_AS_DICT['name'])

    self.assertTestServerPresenceOnPage(True, False)
    landing_url = self.args.server_url + flask.url_for('landing')
    self.assertEquals(landing_url, self.driver.current_url)

  def testRepeatedSearchesFromLandingPage(self):
    """Test that search displays results within the landing page."""
    landing_url = self.args.server_url + flask.url_for('landing')

    # Add user and server.
    landing_page = LandingPage(self.driver)
    landing_page.addTestUser(BaseTest.TEST_USER_AS_DICT['name'],
                             BaseTest.TEST_USER_AS_DICT['email'],
                             self.args.server_url)
    landing_page.addTestServer(BaseTest.TEST_SERVER_AS_DICT['ip'],
                               BaseTest.TEST_SERVER_AS_DICT['name'],
                               BaseTest.TEST_SERVER_AS_DICT['ssh_private_key'],
                               BaseTest.TEST_SERVER_AS_DICT['host_public_key'],
                               self.args.server_url)

    # Verify they both show up.
    self.assertTestUserPresenceOnPage(True)
    self.assertTestServerPresenceOnPage(True)

    # Search for a server.
    landing_page.searchForTestItem(BaseTest.TEST_SERVER_AS_DICT['name'])

    # Verify the server was found and the user was not.
    self.assertTestUserPresenceOnPage(False, False)
    self.assertTestServerPresenceOnPage(True, False)

    # Verify we are still on the landing page.
    self.assertEquals(landing_url, self.driver.current_url)

    # Search for a user.
    landing_page.searchForTestItem(BaseTest.TEST_USER_AS_DICT['name'])

    # Verify the user was found and the server was not.
    self.assertTestUserPresenceOnPage(True, False)
    self.assertTestServerPresenceOnPage(False, False)

    # Verify we are still on the landing page.
    self.assertEquals(landing_url, self.driver.current_url)

  def testSearchUserFromSetupPage(self):
    """Test that search displays user results on a new page."""
    setup_page = SetupPage(self.driver)
    setup_page.addTestUser(BaseTest.TEST_USER_AS_DICT['name'],
                           BaseTest.TEST_USER_AS_DICT['email'],
                           self.args.server_url)
    self.assertTestUserPresenceOnPage(True)
    self.driver.get(self.args.server_url + flask.url_for('setup'))

    setup_page.searchForTestItem(BaseTest.TEST_USER_AS_DICT['name'])

    self.assertTestUserPresenceOnPage(True, False)
    search_url = self.args.server_url + flask.url_for('search_page')
    self.assertTrue(self.driver.current_url.startswith(search_url))

  def testSearchServerFromSetupPage(self):
    """Test that search displays server results on a new page."""
    setup_page = SetupPage(self.driver)
    setup_page.addTestServer(BaseTest.TEST_SERVER_AS_DICT['ip'],
                             BaseTest.TEST_SERVER_AS_DICT['name'],
                             BaseTest.TEST_SERVER_AS_DICT['ssh_private_key'],
                             BaseTest.TEST_SERVER_AS_DICT['host_public_key'],
                             self.args.server_url)
    self.assertTestServerPresenceOnPage(True)
    self.driver.get(self.args.server_url + flask.url_for('setup'))

    setup_page.searchForTestItem(BaseTest.TEST_SERVER_AS_DICT['name'])

    self.assertTestServerPresenceOnPage(True, False)
    search_url = self.args.server_url + flask.url_for('search_page')
    self.assertTrue(self.driver.current_url.startswith(search_url))

  def testRepeatedSearchesFromSetupToSearchPage(self):
    """Test that search displays results within the new page."""
    search_url = self.args.server_url + flask.url_for('search_page')

    # Add user and server.
    setup_page = SetupPage(self.driver)
    setup_page.addTestUser(BaseTest.TEST_USER_AS_DICT['name'],
                           BaseTest.TEST_USER_AS_DICT['email'],
                           self.args.server_url)
    setup_page.addTestServer(BaseTest.TEST_SERVER_AS_DICT['ip'],
                             BaseTest.TEST_SERVER_AS_DICT['name'],
                             BaseTest.TEST_SERVER_AS_DICT['ssh_private_key'],
                             BaseTest.TEST_SERVER_AS_DICT['host_public_key'],
                             self.args.server_url)

    # Verify they both show up.
    self.assertTestUserPresenceOnPage(True)
    self.assertTestServerPresenceOnPage(True)

    # Go to setup so we will get redirected to search page.
    self.driver.get(self.args.server_url + flask.url_for('setup'))

    # Search for a server.
    setup_page.searchForTestItem(BaseTest.TEST_SERVER_AS_DICT['name'])

    # Verify the server was found and the user was not.
    self.assertTestUserPresenceOnPage(False, False)
    self.assertTestServerPresenceOnPage(True, False)

    # Verify we are on the search page now.
    self.assertTrue(self.driver.current_url.startswith(search_url))

    # Search for a user.
    setup_page.searchForTestItem(BaseTest.TEST_USER_AS_DICT['name'])

    # Verify the user was found and the server was not.
    self.assertTestUserPresenceOnPage(True, False)
    self.assertTestServerPresenceOnPage(False, False)

    # Verify we are still on the search page.
    self.assertTrue(self.driver.current_url.startswith(search_url))


if __name__ == '__main__':
  unittest.main()
