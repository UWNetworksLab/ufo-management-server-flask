"""Sidebar module to get links for testing."""
from base_driver import BaseDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class Sidebar(BaseDriver):

  """Sidebar action methods and locators."""

  # pylint: disable=too-few-public-methods

  SIDEBAR = (By.TAG_NAME, 'ufo-sidebar')

  HOME_LINK = (By.ID, 'Home')
  USERS_LINK = (By.ID, 'Users')
  PROXY_SERVERS_LINK = (By.ID, 'Proxy Servers')
  CHROME_POLICY_LINK = (By.ID, 'Chrome Policy')
  SETUP_LINK = (By.ID, 'Setup')
  LOGOUT_LINK = (By.ID, 'Logout')


  def GetLink(self, link_locator):
    """Get an element in the sidebar based on the link locator given."""
    # return self.driver.find_element(*link_locator)
    return WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(((link_locator))))
