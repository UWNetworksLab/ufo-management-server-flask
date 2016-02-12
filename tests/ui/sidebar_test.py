"""Test sidebar module functionality."""
import unittest

from base_test import BaseTest
from sidebar import Sidebar

import flask


class SidebarTest(BaseTest):

  """Test sidebar partial page functionality."""

  def setUp(self):
    """Setup for test methods."""
    super(SidebarTest, self).setUp()
    super(SidebarTest, self).setContext()

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

    chrome_policy_link = sidebar.GetLink(sidebar.CHROME_POLICY_LINK)
    self.assertEquals(flask.url_for('chrome_policy'),
                      chrome_policy_link.get_attribute('data-href'))

    setup_link = sidebar.GetLink(sidebar.SETUP_LINK)
    self.assertEquals(flask.url_for('setup'),
                      setup_link.get_attribute('data-href'))

    logout_link = sidebar.GetLink(sidebar.LOGOUT_LINK)
    self.assertEquals('/logout/', logout_link.get_attribute('data-href'))


if __name__ == '__main__':
  unittest.main()
