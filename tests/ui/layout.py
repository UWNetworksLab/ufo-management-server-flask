"""Layout module to abstract away the sidebar and future common elements."""

from selenium.webdriver.common.by import By

from base_driver import BaseDriver
from sidebar import Sidebar

class UfOPageLayout(BaseDriver):

  """Page layout class with a sidebar and to hold future common elements."""

  # pylint: disable=too-few-public-methods

  MAIN_TOOLBAR = (By.ID, 'main-toolbar')
  LANDING_ANCHOR = (By.ID, 'logoLandingAnchor')
  SEARCH_FORM = (By.ID, 'searchForm')
  SEARCH_BUTTON = (By.ID, 'searchButton')
  OPEN_MENU_BUTTON = (By.ID, 'openMenuButton')
  MAIN_HOLDER = (By.ID, 'main-holder')
  JIGSAW_LOGO_HOLDER = (By.ID, 'jigsaw-logo-holder')
  BASE_PAGE_ELEMENTS = [
    MAIN_TOOLBAR,
    LANDING_ANCHOR,
    SEARCH_FORM,
    SEARCH_BUTTON,
    OPEN_MENU_BUTTON,
    MAIN_HOLDER,
    JIGSAW_LOGO_HOLDER
  ]

  SEARCH_SPINNER = (By.ID, 'searchSpinner')

  USER_DISPLAY_TEMPLATE = (By.ID, 'userDisplayTemplate')
  PROXY_SERVER_DISPLAY_TEMPLATE = (By.ID, 'proxyServerDisplayTemplate')
  OAUTH_DISPLAY_TEMPLATE = (By.ID, 'oauthDisplayTemplate')
  CHROME_POLICY_DISPLAY_TEMPLATE = (By.ID, 'chromePolicyDisplayTemplate')
  SETTINGS_DISPLAY_TEMPLATE = (By.ID, 'settingsDisplayTemplate')

  ADD_USER_BUTTON = (By.ID, 'addUserButton')
  USER_LIST_ITEM = (By.ID, 'userList')
  GENERIC_LISTBOX = (By.TAG_NAME, 'paper-listbox')

  ADD_MANUALLY_TAB = (By.ID, 'manualAddTab')
  ADD_MANUALLY_FORM = (By.ID, 'manualAdd')
  ADD_MANUALLY_INPUT_NAME = (By.ID, 'manualUserName')
  ADD_MANUALLY_INPUT_EMAIL = (By.ID, 'manualUserEmail')
  ADD_MANUALLY_SUBMIT_BUTTON = (By.ID, 'manualAddSubmitButton')
  ADD_MANUALLY_SPINNER = (By.ID, 'manualAddSpinner')

  DETAILS_MODAL = (By.TAG_NAME, 'paper-dialog')

  USER_DELETE_BUTTON = (By.ID, 'userDeleteButton')
  USER_DISABLE_ENABLE_TEXT = (By.ID, 'isEnabledDisabledText')
  USER_DISABLE_ENABLE_BUTTON = (By.ID, 'userDisableEnableButton')
  USER_INVITE_CODE_TEXT = (By.ID, 'lastInviteCode')
  USER_COPY_INVITE_BUTTON = (By.ID, 'copyInviteCodeButton')
  USER_ROTATE_KEYS_BUTTON = (By.ID, 'rotateKeysButton')
  USER_DETAILS_SPINNER = (By.ID, 'userDetailsSpinner')

  ADD_SERVER_BUTTON = (By.ID, 'addServerButton')
  SERVER_LIST_ITEM = (By.ID, 'proxyList')

  ADD_SERVER_MODAL = (By.ID, 'serverModal')
  ADD_SERVER_FORM = (By.ID, 'serverAddForm')
  ADD_SERVER_INPUT_IP = (By.ID, 'ipInput')
  ADD_SERVER_INPUT_NAME = (By.ID, 'nameInput')
  ADD_SERVER_INPUT_PRIVATE_KEY = (By.ID, 'privateKeyInput')
  ADD_SERVER_INPUT_PUBLIC_KEY = (By.ID, 'publicKeyInput')
  ADD_SERVER_SUBMIT_BUTTON = (By.ID, 'serverAddSubmitButton')
  ADD_SERVER_SPINNER = (By.ID, 'serverSpinner')

  SERVER_DELETE_BUTTON = (By.ID, 'serverDeleteButton')
  SERVER_DELETE_SPINNER = (By.ID, 'serverDetailsSpinner')

  CHROME_POLICY_DOWNLOAD_BUTTON = (By.ID, 'chromePolicyDownloadButton')

  def GetSearchBar(self):
    """Get the search bar element on the page.

    Returns:
      The sidebar element for any page.
    """
    return self.driver.find_element(*UfOPageLayout.SEARCH_FORM)
