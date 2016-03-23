"""Landing page module for testing."""

from selenium.webdriver.common.by import By

from layout import UfOPageLayout

class LandingPage(UfOPageLayout):

  """Home page action methods and locators."""

  # pylint: disable=too-few-public-methods

  USER_DISPLAY_TEMPLATE = (By.ID, 'userDisplayTemplate')
  PROXY_SERVER_DISPLAY_TEMPLATE = (By.ID, 'proxyServerDisplayTemplate')
  CHROME_POLICY_DISPLAY_TEMPLATE = (By.ID, 'chromePolicyDisplayTemplate')
  LANDING_PAGE_ELEMENTS = [
    USER_DISPLAY_TEMPLATE,
    PROXY_SERVER_DISPLAY_TEMPLATE,
    CHROME_POLICY_DISPLAY_TEMPLATE
  ]
