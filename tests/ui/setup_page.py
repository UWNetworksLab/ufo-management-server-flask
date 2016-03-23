"""Setup page module functionality for getting elements for testing."""

from selenium.webdriver.common.by import By

from layout import UfOPageLayout


class SetupPage(UfOPageLayout):

  """Setup page action methods and locators."""

  # pylint: disable=too-few-public-methods

  USER_DISPLAY_TEMPLATE = (By.ID, 'userDisplayTemplate')
  PROXY_SERVER_DISPLAY_TEMPLATE = (By.ID, 'proxyServerDisplayTemplate')
  OAUTH_DISPLAY_TEMPLATE = (By.ID, 'oauthDisplayTemplate')
  CHROME_POLICY_DISPLAY_TEMPLATE = (By.ID, 'chromePolicyDisplayTemplate')
  SETTINGS_DISPLAY_TEMPLATE = (By.ID, 'settingsDisplayTemplate')
  SETUP_PAGE_ELEMENTS = [
    USER_DISPLAY_TEMPLATE,
    PROXY_SERVER_DISPLAY_TEMPLATE,
    OAUTH_DISPLAY_TEMPLATE,
    CHROME_POLICY_DISPLAY_TEMPLATE,
    SETTINGS_DISPLAY_TEMPLATE
  ]
