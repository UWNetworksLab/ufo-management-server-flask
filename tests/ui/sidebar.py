"""Sidebar module to get links for testing."""
from base_driver import BaseDriver

from selenium.webdriver.common.by import By

class Sidebar(BaseDriver):

  """Sidebar action methods and locators."""

  # pylint: disable=too-few-public-methods

  HOME_LINK = (By.ID, 'Home')
  USERS_LINK = (By.ID, 'Users')
  PROXY_SERVERS_LINK = (By.ID, 'Proxy Servers')
  SETUP_LINK = (By.ID, 'Setup')
  LOGOUT_LINK = (By.ID, 'Logout')
