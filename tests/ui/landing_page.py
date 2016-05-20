"""Landing page module for testing."""

import flask
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from server_form import ServerForm
from add_user_form import AddUserForm
from layout import UfOPageLayout

class LandingPage(UfOPageLayout):

  """Home page action methods and locators."""

  LANDING_PAGE_ELEMENTS = [
    UfOPageLayout.USER_DISPLAY_TEMPLATE,
    UfOPageLayout.PROXY_SERVER_DISPLAY_TEMPLATE,
    UfOPageLayout.CHROME_POLICY_DISPLAY_TEMPLATE
  ]

  def addTestUser(self, name, email, server_url):
    """Manually add a test user using the landing page.

    Args:
      name: A string for the name of a test user.
      email: A string for the email of a test user.
      server_url: The base url portion of the landing page.
    """
    # Navigate to add user and go to manual tab.
    self.driver.get(server_url + flask.url_for('landing'))
    add_user_button = self.GetElement(UfOPageLayout.ADD_USER_BUTTON)
    add_user_button.click()
    add_manually_tab = WebDriverWait(self.driver,
                                     UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((UfOPageLayout.ADD_MANUALLY_TAB))))
    add_manually_tab.click()

    add_user_form = AddUserForm(self.driver)
    add_user_form.addTestUser(name, email)

  def removeTestUser(self, name, server_url, should_raise_exception=True):
    """Manually remove a test user using the landing page (the only way).

    Args:
      name: A string for the name of the test user to remove.
      server_url: The base url portion of the landing page.
      should_raise_exception: True to raise an exception if the user is not
                              found.
    """
    # Find the user and navigate to their details page.
    self.driver.get(server_url + flask.url_for('landing'))
    user_item = self.findTestUser(name)

    if user_item is None:
      if should_raise_exception:
        raise Exception
      else:
        return
    else:
      user_item.click()

    # Click delete on that user.
    details_modal = user_item.find_element(*LandingPage.DETAILS_MODAL)
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of(details_modal))
    delete_button = details_modal.find_element(*LandingPage.USER_DELETE_BUTTON)
    delete_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            LandingPage.USER_DETAILS_SPINNER))))

  def findTestUser(self, name):
    """Find the test user on the landing page if it exists.

    Args:
      name: A string for the name of the test user to find.

    Returns:
      The anchor element for visiting the given item's details page or None.
    """
    landing_page = LandingPage(self.driver)
    user_list_item = landing_page.GetElement(LandingPage.USER_LIST_ITEM)
    user_listbox = user_list_item.find_element(*LandingPage.GENERIC_LISTBOX)
    return self.findItemInListing(user_listbox, name)

  def addTestServer(self, ip, name, private_key, public_key, server_url):
    """Add a test server using the landing page.

    Args:
      ip: A string for the ip address of the server to add.
      name: A string for the name of the server to add.
      private_key: A string for the private key of the server to add.
      public_key: A string for the public key of the server to add.
      server_url: The base url portion of the setup page.
    """
    # Navigate to add server.
    self.driver.get(server_url + flask.url_for('landing'))
    add_server_button = self.GetElement(UfOPageLayout.ADD_SERVER_BUTTON)
    add_server_button.click()
    add_server_modal = WebDriverWait(self.driver,
                                     UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((UfOPageLayout.ADD_SERVER_MODAL))))

    server_form = ServerForm(self.driver)
    server_form.addServer(add_server_modal, ip, name, private_key, public_key)

  def removeTestServer(self, name, server_url, should_raise_exception=True):
    """Remove a test server using the landing page (the only way).

    Args:
      name: A string for the name of the test server to remove.
      server_url: The base url portion of the landing page.
      should_raise_exception: True to raise an exception if the server is not
                              found.
    """
    # Find the server and navigate to its details page.
    self.driver.get(server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    server_list = landing_page.GetElement(LandingPage.SERVER_LIST_ITEM)
    server_listbox = server_list.find_element(*LandingPage.GENERIC_LISTBOX)
    server_item = landing_page.findItemInListing(server_listbox, name)

    if server_item is None:
      if should_raise_exception:
        raise Exception
      else:
        return
    else:
      server_item.click()

    # Click delete on that server.
    details_modal = server_item.find_element(*LandingPage.DETAILS_MODAL)
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of(details_modal))
    delete_button = details_modal.find_element(
        *LandingPage.SERVER_DELETE_BUTTON)
    delete_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            LandingPage.SERVER_DETAILS_SPINNER))))

  def editTestServer(self, old_name, ip, name, ssh_private_key, host_public_key,
                     server_url):
    """Edit a test server using the landing page (the only way).

    Args:
      old_name: A string for the name of the test server to edit.
      ip: A string for the ip address of the server to insert.
      name: A string for the name of the server to insert.
      ssh_private_key: A string for the ssh private key of the server to insert.
      host_public_key: A string for the host public key of the server to insert.
      server_url: The base url portion of the landing page.
    """
    # Find the server and navigate to its details page.
    self.driver.get(server_url + flask.url_for('landing'))
    landing_page = LandingPage(self.driver)
    server_list = landing_page.GetElement(LandingPage.SERVER_LIST_ITEM)
    server_listbox = server_list.find_element(*LandingPage.GENERIC_LISTBOX)
    server_item = landing_page.findItemInListing(server_listbox, old_name)

    if server_item is None:
      raise Exception
    else:
      server_item.click()

    # Click edit on that server.
    details_modal = server_item.find_element(*LandingPage.DETAILS_MODAL)
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of(details_modal))
    edit_button = details_modal.find_element(*LandingPage.SERVER_EDIT_BUTTON)
    edit_button.click()

    # Perform the actual edits
    server_form = ServerForm(self.driver)
    server_form.editServer(details_modal, ip, name, ssh_private_key,
                           host_public_key)

  def getContainerElementForItem(self, item, should_use_listbox):
    """Given an item, get the container element for it based on the boolean.

    I realize this method is very basic, but it is just to avoid a lot of
    duplication across some tests.

    Args:
      item: The item whose container needs to be returned.
      should_use_listbox: If true, this will just return the item itself.
                          Otherwise, this will open and return the details
                          dialog.

    Returns:
      The container for the given element based on should_use_listbox, either
      the item itself or its details dialog once opened.
    """
    if should_use_listbox:
      # Hover the item so the button shows up.
      ActionChains(self.driver).move_to_element(item).perform()
      return item
    else:
      return self.getDetailsDialogForItem(item)

  def getDetailsDialogForItem(self, item):
    """Given an item, open it's details dialog and return that element.

    Args:
      item: The item whose details dialog needs to be opened.

    Returns:
      The details dialog for the given element, once opened.
    """
    item.click()
    details_modal = item.find_element(*LandingPage.DETAILS_MODAL)
    WebDriverWait(self.driver, LandingPage.DEFAULT_TIMEOUT).until(
        EC.visibility_of(details_modal))
    return details_modal

  def clickDisableEnableOnUserElement(self, element):
    """Given a user element, click the disable/enable button on it.

    Args:
      element: The user element to click disable/enable upon.
    """
    disable_enable_button = element.find_element(
        *LandingPage.USER_DISABLE_ENABLE_BUTTON)
    disable_enable_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, LandingPage.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            LandingPage.USER_DETAILS_SPINNER))))
