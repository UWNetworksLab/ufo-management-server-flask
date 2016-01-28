"""Landing page module for testing."""
from base_driver import BaseDriver

from selenium.webdriver.common.by import By

class LandingPage(BaseDriver):

  """Home page action methods and locators."""

  # pylint: disable=too-few-public-methods

  TITLE = (By.TAG_NAME, 'h2')
  INSTRUCTION = (By.TAG_NAME, 'h4')
