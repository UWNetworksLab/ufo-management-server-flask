"""Admin module for testing."""

import flask
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from layout import UfOPageLayout

class AdminFlow(UfOPageLayout):

  """Admin flow methods and locators."""

  LANDING_PAGE_ELEMENTS = [
    UfOPageLayout.USER_DISPLAY_TEMPLATE,
    UfOPageLayout.PROXY_SERVER_DISPLAY_TEMPLATE,
    UfOPageLayout.CHROME_POLICY_DISPLAY_TEMPLATE
  ]

  def getAddAdminDialog(self, dropdown_menu):
    """Navigates to the add admin dialog on a given page.

    Args:
      dropdown_menu: The dropdown menu to navigate upon.

    Returns:
      The add admin dialog element once found.
    """
    add_admin_button = dropdown_menu.find_element(
        *UfOPageLayout.ADD_ADMIN_BUTTON)
    add_admin_button.click()

    add_admin_dialog = WebDriverWait(self.driver,
                                     UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((
            UfOPageLayout.ADD_ADMIN_DIALOG))))
    return add_admin_dialog

  def getRemoveAdminDialog(self, dropdown_menu):
    """Navigates to the remove admin dialog on a given page.

    Args:
      dropdown_menu: The dropdown menu to navigate upon.

    Returns:
      The remove admin dialog element once found.
    """
    remove_admin_button = dropdown_menu.find_element(
        *UfOPageLayout.REMOVE_ADMIN_BUTTON)
    remove_admin_button.click()

    remove_admin_dialog = WebDriverWait(self.driver,
                                        UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((
            UfOPageLayout.REMOVE_ADMIN_DIALOG))))
    return remove_admin_dialog

  def findTestAdminOnRemoveForm(self, username, remove_admin_form):
    """Find and return the test admin element on the remove admin form.

    Args:
      username: A string for the username of the test admin to find.
      remove_admin_form: The remove admin form to search through.

    Returns:
      The test admin element once found.
    """
    menu = remove_admin_form.find_element(By.TAG_NAME, 'paper-menu')
    return self.findItemInListing(menu, username,
                                  should_find_by_icon_item=False)

  def addTestAdmin(self, username, password, add_admin_dialog):
    """Add a test admin account using the add admin form.

    Args:
      username: A string for the username of the test admin to add.
      passwprd: A string for the password of the test admin to add.
      add_admin_dialog: The add admin dialog element to find the add form on.
    """
    add_admin_form = add_admin_dialog.find_element(
        *UfOPageLayout.ADD_ADMIN_FORM)
    username_paper_input = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_USERNAME)
    username_input = username_paper_input.find_element(By.ID, 'input')
    username_input.send_keys(username)

    password_paper_input = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_PASSWORD)
    password_input = password_paper_input.find_element(By.ID, 'input')
    password_input.send_keys(password)

    submit_button = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_SUBMIT)
    submit_button.click()

    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.DROPDOWN_MENU_SPINNER))))

  def removeTestAdmin(self, username, server_url, should_raise_exception=True):
    """Remove a test admin account using a form post (the only way currently).

    Args:
      username: A string for the username of the test admin to remove.
      server_url: The base url portion of the landing page.
      should_raise_exception: True to raise an exception if the admin is not
                              found.
    """
    # Find the user and navigate to their details page.
    self.driver.get(server_url + flask.url_for('landing'))
    dropdown_menu = self.getDropdownMenu()
    remove_admin_dialog = self.getRemoveAdminDialog(dropdown_menu)
    remove_admin_form = remove_admin_dialog.find_element(
        *UfOPageLayout.REMOVE_ADMIN_FORM)
    admin_item = self.findTestAdminOnRemoveForm(username, remove_admin_form)

    if admin_item is None:
      if should_raise_exception:
        raise Exception
      else:
        return
    else:
      admin_item.click()

    # Click the delete button with that admin selected.
    submit_button = remove_admin_dialog.find_element(
        *UfOPageLayout.REMOVE_ADMIN_SUBMIT)
    submit_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.DROPDOWN_MENU_SPINNER))))
