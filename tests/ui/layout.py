"""Layout module to abstract away the sidebar and future common elements."""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base_driver import BaseDriver

class UfOPageLayout(BaseDriver):

  """Page layout class with a sidebar and to hold future common elements."""

  # pylint: disable=too-few-public-methods

  MAIN_TOOLBAR = (By.ID, 'main-toolbar')
  LANDING_ANCHOR = (By.ID, 'logoLandingAnchor')
  SEARCH_FORM = (By.ID, 'searchForm')
  SEARCH_BUTTON = (By.ID, 'searchButton')
  OPEN_MENU_BUTTON = (By.ID, 'openMenuButton')
  MAIN_HOLDER = (By.ID, 'main-holder')
  BASE_PAGE_ELEMENTS_FOR_LOGIN = [
    MAIN_TOOLBAR,
    LANDING_ANCHOR,
    MAIN_HOLDER
  ]
  BASE_PAGE_ELEMENTS_AFTER_LOGIN = [
    SEARCH_FORM,
    SEARCH_BUTTON,
    OPEN_MENU_BUTTON
  ]
  BASE_PAGE_ELEMENTS = (BASE_PAGE_ELEMENTS_FOR_LOGIN +
                        BASE_PAGE_ELEMENTS_AFTER_LOGIN)

  SEARCH_SPINNER = (By.ID, 'searchSpinner')

  DROPDOWN_MENU = (By.ID, 'ufoDropdownMenu')
  DROPDOWN_MENU_SPINNER = (By.ID, 'dropdownMenuSpinner')
  ADD_ADMIN_BUTTON = (By.ID, 'addAdminButton')
  ADD_ADMIN_DIALOG = (By.ID, 'addAdminDialog')
  ADD_ADMIN_FORM = (By.ID, 'addAdminForm')
  ADD_ADMIN_EMAIL = (By.ID, 'paperAdminEmail')
  ADD_ADMIN_PASSWORD = (By.ID, 'paperAdminPassword')
  ADD_ADMIN_SUBMIT = (By.ID, 'adminFormSubmitButton')
  ADD_ADMIN_RESPONSE_STATUS = (By.ID, 'addAdminResponseStatus')
  REMOVE_ADMIN_DIALOG = (By.ID, 'removeAdminDialog')
  REMOVE_ADMIN_BUTTON = (By.ID, 'removeAdminButton')
  REMOVE_ADMIN_FORM = (By.ID, 'removeAdminForm')
  REMOVE_ADMIN_SUBMIT = (By.ID, 'removeAdminSubmitButton')
  SETTINGS_ANCHOR = (By.ID, 'settingsAnchor')

  USER_DISPLAY_TEMPLATE = (By.ID, 'userDisplayTemplate')
  PROXY_SERVER_DISPLAY_TEMPLATE = (By.ID, 'proxyServerDisplayTemplate')
  OAUTH_DISPLAY_TEMPLATE = (By.ID, 'oauthDisplayTemplate')
  CHROME_POLICY_DISPLAY_TEMPLATE = (By.ID, 'chromePolicyDisplayTemplate')

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
  ADD_SERVER_SUBMIT_BUTTON = (By.ID, 'serverAddSubmitButton')
  ADD_SERVER_SPINNER = (By.ID, 'serverSpinner')

  EDIT_SERVER_FORM = (By.ID, 'serverEditForm')
  EDIT_SERVER_SUBMIT_BUTTON = (By.ID, 'serverEditSubmitButton')

  # These are shared between the add and edit flows for simplicity.
  SERVER_INPUT_IP = (By.ID, 'ipInput')
  SERVER_INPUT_NAME = (By.ID, 'nameInput')
  SERVER_INPUT_PRIVATE_KEY = (By.ID, 'privateKeyInput')
  SERVER_INPUT_PUBLIC_KEY = (By.ID, 'publicKeyInput')

  SERVER_DELETE_BUTTON = (By.ID, 'serverDeleteButton')
  SERVER_DETAILS_BUTTON = (By.ID, 'serverDetailsButton')
  SERVER_EDIT_BUTTON = (By.ID, 'serverEditButton')
  SERVER_DETAILS_SPINNER = (By.ID, 'serverDetailsSpinner')

  CHROME_POLICY_DOWNLOAD_BUTTON = (By.ID, 'chromePolicyDownloadButton')


  def GetSearchBar(self):
    """Get the search bar element on the page.

    Returns:
      The sidebar element for any page.
    """
    return self.driver.find_element(*UfOPageLayout.SEARCH_FORM)

  def findItemInListing(self, listing, name, should_find_by_icon_item=True):
    """Given the listing of items and a name, return the name's anchor.

    Args:
      listing: The paper-listbox element holding all items.
      name: The name of an item to search for.
      should_find_by_icon_item: True if the items to search are icon items.
                                False for regular items.

    Returns:
      The anchor element for visiting the given item's details page or None.
    """
    items = None
    if should_find_by_icon_item:
      items = listing.find_elements(By.TAG_NAME, 'paper-icon-item')
    else:
      items = listing.find_elements(By.TAG_NAME, 'paper-item')
    for item in items:
      # This can technically return multiple, but it will only return one.
      container_element = item
      if should_find_by_icon_item:
        container_element = item.find_elements(By.CLASS_NAME, 'first-div')[0]
      strong = container_element.find_elements(By.TAG_NAME, 'strong')[0]
      if name.lower() in strong.text.lower():
        return item
    return None

  def searchForTestItem(self, name):
    """Execute a search for the test item from the current page.

    Args:
      name: A string for the name of the item to search for.
    """
    generic_page = UfOPageLayout(self.driver)
    search_bar = generic_page.GetSearchBar()
    search_input = search_bar.find_element(By.ID, 'input')
    existing_search_text = search_input.get_attribute('value')
    for x in range(len(existing_search_text)):
      search_input.send_keys(Keys.BACKSPACE)
    search_input.send_keys(name)

    search_button = search_bar.find_element(*UfOPageLayout.SEARCH_BUTTON)
    search_button.click()

    # Wait for search to finish, can take a while.
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.SEARCH_SPINNER))))

  def getDropdownMenu(self):
    """Navigates to the dropdown menu on a given page.

    Returns:
      The dropdown menu element once found.
    """
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((UfOPageLayout.OPEN_MENU_BUTTON))))
    dropdown_button = self.driver.find_element(*UfOPageLayout.OPEN_MENU_BUTTON)
    dropdown_button.click()

    dropdown_menu = WebDriverWait(self.driver,
                                  UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((UfOPageLayout.DROPDOWN_MENU))))
    return dropdown_menu
