"""Landing page module for testing."""
from layout import UfOPageLayout

from selenium.webdriver.common.by import By

class LandingPage(UfOPageLayout):

  """Home page action methods and locators."""

  # pylint: disable=too-few-public-methods

  TITLE = (By.TAG_NAME, 'h2')
  INSTRUCTION = (By.TAG_NAME, 'h4')
