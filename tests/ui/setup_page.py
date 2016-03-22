"""Setup page module functionality for getting elements for testing."""

from selenium.webdriver.common.by import By

from layout import UfOPageLayout


class SetupPage(UfOPageLayout):

  """Setup page action methods and locators."""

  # pylint: disable=too-few-public-methods

  ADD_USERS_LINK = (By.ID, 'add_users')
  USER_LISTING = (By.TAG_NAME, 'paper-listbox')

  ADD_USERS_TABS = (By.ID, 'tabsContent')
  ADD_MANUALLY_TAB = (By.XPATH, '//div[text()="Add Manually"]')
  ADD_MANUALLY_FORM = (By.ID, 'users-manual-form')
  ADD_MANUALLY_INPUT_NAME = (By.NAME, 'name')
  ADD_MANUALLY_INPUT_EMAIL = (By.NAME, 'email')
  SUBMIT_BUTTON = (By.TAG_NAME, 'paper-button')

  DELETE_FORM = (By.ID, 'user-delete-form')
