"""Setup page module functionality for getting elements for testing."""

from selenium.webdriver.common.by import By

from layout import UfOPageLayout


class SetupPage(UfOPageLayout):

  """Setup page action methods and locators."""

  # pylint: disable=too-few-public-methods

  SETUP_PAGE_ELEMENTS = [
    UfOPageLayout.USER_DISPLAY_TEMPLATE,
    UfOPageLayout.PROXY_SERVER_DISPLAY_TEMPLATE,
    UfOPageLayout.OAUTH_DISPLAY_TEMPLATE,
    UfOPageLayout.CHROME_POLICY_DISPLAY_TEMPLATE,
    UfOPageLayout.SETTINGS_DISPLAY_TEMPLATE
  ]
