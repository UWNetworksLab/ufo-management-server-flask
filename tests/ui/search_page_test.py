"""Test search page module functionality."""
import unittest

import flask

from base_test import BaseTest
from login_page import LoginPage
from search_page import SearchPage


class SearchPageTest(BaseTest):

  """Test search page functionality."""

  def setUp(self):
    """Search for test methods."""
    super(SearchPageTest, self).setUp()
    super(SearchPageTest, self).setContext()
    LoginPage(self.driver).Login(self.args)

  def tearDown(self):
    """Teardown for test methods."""
    self.removeTestUser(should_raise_exception=False)
    self.removeTestServer(should_raise_exception=False)
    LoginPage(self.driver).Logout(self.args)
    super(SearchPageTest, self).tearDown()

  def testSearchPageLayout(self):
    """Test the search page layout contains the elements we expect.

    This should include elements inherited from the base page,
    BASE_PAGE_ELEMENTS (defined in layout.py), as well as elements specific to
    the search page, SEARCH_PAGE_ELEMENTS. Please add to each list as the UI
    is modified to ensure this test stays up to date.
    """
    self.searchForTestItem()

    search_page = SearchPage(self.driver)
    for element_by_id in SearchPage.BASE_PAGE_ELEMENTS:
      base_page_element = search_page.GetElement(element_by_id)
      self.assertIsNotNone(base_page_element)

    self.assertLogoLinksToLandingPage()

    for element_by_id in SearchPage.SEARCH_PAGE_ELEMENTS:
      search_page_element = search_page.GetElement(element_by_id)
      self.assertIsNotNone(search_page_element)

  def testSearchUserFromLandingPage(self):
    """Test that search displays user results within the landing page."""
    self.addTestUserFromLandingPage()
    self.assertTestUserPresenceOnPage(True)

    self.searchForTestItem()

    self.assertTestUserPresenceOnPage(True, False)
    landing_url = self.args.server_url + flask.url_for('landing')
    self.assertEquals(landing_url, self.driver.current_url)

  def testSearchServerFromLandingPage(self):
    """Test that search displays server results within the landing page."""
    self.addTestServerFromLandingPage()
    self.assertTestServerPresenceOnPage(True)

    self.searchForTestItem(is_user=False)

    self.assertTestServerPresenceOnPage(True, False)
    landing_url = self.args.server_url + flask.url_for('landing')
    self.assertEquals(landing_url, self.driver.current_url)

  def testSearchUserFromSetupPage(self):
    """Test that search displays user results on a new page."""
    self.addTestUserFromSetupPage()
    self.assertTestUserPresenceOnPage(True)
    self.driver.get(self.args.server_url + flask.url_for('setup'))

    self.searchForTestItem()

    self.assertTestUserPresenceOnPage(True, False)
    search_url = self.args.server_url + flask.url_for('search_page')
    self.assertTrue(self.driver.current_url.startswith(search_url))

  def testSearchServerFromSetupPage(self):
    """Test that search displays server results on a new page."""
    self.addTestServerFromSetupPage()
    self.assertTestServerPresenceOnPage(True)
    self.driver.get(self.args.server_url + flask.url_for('setup'))

    self.searchForTestItem(is_user=False)

    self.assertTestServerPresenceOnPage(True, False)
    search_url = self.args.server_url + flask.url_for('search_page')
    self.assertTrue(self.driver.current_url.startswith(search_url))


if __name__ == '__main__':
  unittest.main()
