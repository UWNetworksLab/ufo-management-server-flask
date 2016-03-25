"""Landing page module for testing."""

from selenium.webdriver.common.by import By

from layout import UfOPageLayout

class LandingPage(UfOPageLayout):

  """Home page action methods and locators."""

  # pylint: disable=too-few-public-methods

  LANDING_PAGE_ELEMENTS = [
    UfOPageLayout.USER_DISPLAY_TEMPLATE,
    UfOPageLayout.PROXY_SERVER_DISPLAY_TEMPLATE,
    UfOPageLayout.CHROME_POLICY_DISPLAY_TEMPLATE
  ]
