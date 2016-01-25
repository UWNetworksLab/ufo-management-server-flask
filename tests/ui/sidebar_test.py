"""Test sidebar module functionality."""
import unittest

from base_test import BaseTest
from sidebar import Sidebar
from test_config import CHROME_DRIVER_LOCATION
from ufo import app

import flask
from selenium import webdriver


class SidebarTest(BaseTest):

  """Test sidebar partial page functionality."""

  def setUp(self):
    """Setup for test methods."""
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    # TODO(eholder) Re-enable this once we have a login module again.
    # LoginPage(self.driver).Login(self.args)
    self.context = app.test_request_context()
    self.context.push()

  def testLinks(self):
    """Make sure all the links are pointed to the correct paths."""
    self.driver.get(self.args.server_url)
    sidebar = Sidebar(self.driver)

    home_link = sidebar.GetLink(sidebar.HOME_LINK)
    self.assertEquals(flask.url_for('landing'),
                      home_link.get_attribute('data-href'))

    users_link = sidebar.GetLink(sidebar.USERS_LINK)
    self.assertEquals(flask.url_for('user_list'),
                      users_link.get_attribute('data-href'))

    proxy_servers_link = sidebar.GetLink(sidebar.PROXY_SERVERS_LINK)
    self.assertEquals(flask.url_for('proxyserver_list'),
                      proxy_servers_link.get_attribute('data-href'))

    setup_link = sidebar.GetLink(sidebar.SETUP_LINK)
    self.assertEquals(flask.url_for('setup'),
                      setup_link.get_attribute('data-href'))

    logout_link = sidebar.GetLink(sidebar.LOGOUT_LINK)
    self.assertEquals('/logout/', logout_link.get_attribute('data-href'))

  def tearDown(self):
    """Teardown for test methods."""
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
