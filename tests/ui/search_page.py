"""Search page module functionality for getting elements for testing."""

from selenium.webdriver.common.by import By

from layout import UfOPageLayout


class SearchPage(UfOPageLayout):

  """Search page action methods and locators."""

  # pylint: disable=too-few-public-methods

  SEARCH_PAGE_ELEMENTS = [
    UfOPageLayout.USER_DISPLAY_TEMPLATE,
    UfOPageLayout.PROXY_SERVER_DISPLAY_TEMPLATE
  ]
