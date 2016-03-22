"""Layout module to abstract away the sidebar and future common elements."""

from selenium.webdriver.common.by import By

from base_driver import BaseDriver
from sidebar import Sidebar

class UfOPageLayout(BaseDriver):

  """Page layout class with a sidebar and to hold future common elements."""

  # pylint: disable=too-few-public-methods

  ADD_USER_BUTTON = (By.ID, 'addUserButton')

  USER_LIST_ITEM = (By.ID, 'userList')
  USER_LISTBOX = (By.TAG_NAME, 'paper-listbox')

  ADD_MANUALLY_TAB = (By.ID, 'manualAddTab')
  ADD_MANUALLY_FORM = (By.ID, 'manualAdd')
  ADD_MANUALLY_INPUT_NAME = (By.ID, 'manualUserName')
  ADD_MANUALLY_INPUT_EMAIL = (By.ID, 'manualUserEmail')
  ADD_MANUALLY_SUBMIT_BUTTON = (By.ID, 'manualAddSubmitButton')
  ADD_MANUALLY_SPINNER = (By.ID, 'manualAddSpinner')

  USER_DETAILS_MODAL = (By.TAG_NAME, 'paper-dialog')
  USER_DELETE_BUTTON = (By.ID, 'userDeleteButton')
  USER_DELETE_SPINNER = (By.ID, 'userDetailsSpinner')

  # ADD_USERS_LINK = (By.ID, 'add_users')

  # ADD_USERS_TABS = (By.ID, 'tabsContent')

  # DELETE_FORM = (By.ID, 'user-delete-form')

  def GetSidebar(self):
    """Get the sidebar element on the user page.

    Returns:
      The sidebar element for any page.
    """
    return self.driver.find_element(*Sidebar.SIDEBAR)
