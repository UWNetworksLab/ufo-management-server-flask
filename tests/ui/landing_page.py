"""Landing page module for testing."""
from sidebar import PageWithSidebar

from selenium.webdriver.common.by import By

class LandingPage(PageWithSidebar):

  """Home page action methods and locators."""

  # pylint: disable=too-few-public-methods

  TITLE = (By.TAG_NAME, 'h2')
  INSTRUCTION = (By.TAG_NAME, 'h4')
