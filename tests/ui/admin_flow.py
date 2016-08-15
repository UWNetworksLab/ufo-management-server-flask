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

  def get_add_admin_dialog(self, dropdown_menu):
    """Navigates to the add admin dialog on a given page.

    Args:
      dropdown_menu: The dropdown menu to navigate upon.

    Returns:
      The add admin dialog element once found.
    """
    add_admin_button = dropdown_menu.find_element(
        *UfOPageLayout.ADD_ADMIN_BUTTON)
    add_admin_button.click()

    add_admin_dialog = WebDriverWait(
        self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
            EC.visibility_of_element_located(((
                UfOPageLayout.ADD_ADMIN_DIALOG))))
    return add_admin_dialog

  def get_change_password_dialog(self, dropdown_menu):
    """Navigates to the change admin password dialog on a given page.

    Args:
      dropdown_menu: The dropdown menu to navigate upon.

    Returns:
      The change admin password dialog element once found.
    """
    change_admin_password_button = dropdown_menu.find_element(
        *UfOPageLayout.CHANGE_ADMIN_PASSWORD_BUTTON)
    change_admin_password_button.click()

    change_admin_password_dialog = WebDriverWait(
        self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
            EC.visibility_of_element_located(((
                UfOPageLayout.CHANGE_ADMIN_PASSWORD_DIALOG))))
    return change_admin_password_dialog

  def get_remove_admin_dialog(self, dropdown_menu):
    """Navigates to the remove admin dialog on a given page.

    Args:
      dropdown_menu: The dropdown menu to navigate upon.

    Returns:
      The remove admin dialog element once found.
    """
    remove_admin_button = dropdown_menu.find_element(
        *UfOPageLayout.REMOVE_ADMIN_BUTTON)
    remove_admin_button.click()

    remove_admin_dialog = WebDriverWait(
        self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
            EC.visibility_of_element_located(((
                UfOPageLayout.REMOVE_ADMIN_DIALOG))))
    return remove_admin_dialog

  def find_test_admin_on_remove_form(self, email, remove_admin_form):
    """Find and return the test admin element on the remove admin form.

    Args:
      email: A string for the email of the test admin to find.
      remove_admin_form: The remove admin form to search through.

    Returns:
      The test admin element once found.
    """
    menu = remove_admin_form.find_element(By.TAG_NAME, 'paper-menu')
    return self.findItemInListing(menu, email,
                                  should_find_by_icon_item=False)

  def add_test_admin(self, email, password, add_admin_dialog):
    """Add a test admin account using the add admin form.

    Args:
      email: A string for the email of the test admin to add.
      password: A string for the password of the test admin to add.
      add_admin_dialog: The add admin dialog element to find the add form on.
    """
    add_admin_form = add_admin_dialog.find_element(
        *UfOPageLayout.ADD_ADMIN_FORM)
    email_paper_input = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_EMAIL)
    email_input = email_paper_input.find_element(By.ID, 'input')
    email_input.send_keys(email)

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

  def change_admin_password(self, old_password, new_password,
                            change_admin_password_dialog):
    """Change the password for an admin account using the dialog passed in.

    Args:
      old_password: A string for the current password of the admin.
      new_password: A string for the new password to set on the admin.
      change_admin_password_dialog: The change admin password dialog element
                                    to find the change admin password form on.
    """
    change_admin_password_form = change_admin_password_dialog.find_element(
        *UfOPageLayout.CHANGE_ADMIN_PASSWORD_FORM)
    old_password_paper_input = change_admin_password_form.find_element(
        *UfOPageLayout.CHANGE_ADMIN_PASSWORD_OLD_PASSWORD)
    old_password_input = old_password_paper_input.find_element(By.ID, 'input')
    old_password_input.send_keys(old_password)

    new_password_paper_input = change_admin_password_form.find_element(
        *UfOPageLayout.CHANGE_ADMIN_PASSWORD_NEW_PASSWORD)
    new_password_input = new_password_paper_input.find_element(By.ID, 'input')
    new_password_input.send_keys(new_password)

    submit_button = change_admin_password_dialog.find_element(
        *UfOPageLayout.CHANGE_ADMIN_PASSWORD_SUBMIT)
    submit_button.click()

    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.DROPDOWN_MENU_SPINNER))))

  def remove_test_admin(self, email, server_url, should_raise_exception=True,
                        should_navigate_to_landing=True):
    """Remove a test admin account using a form post (the only way currently).

    Args:
      email: A string for the email of the test admin to remove.
      server_url: The base url portion of the landing page.
      should_raise_exception: True to raise an exception if the admin is not
                              found.
      should_navigate_to_landing: Boolean for whether to go to the landing page
                                  to remove the admin or not.
    """
    # Find the admin on the dropdown dialog.
    if should_navigate_to_landing:
      self.driver.get(server_url + flask.url_for('landing'))
    dropdown_menu = self.getDropdownMenu()
    remove_admin_dialog = self.get_remove_admin_dialog(dropdown_menu)
    remove_admin_form = remove_admin_dialog.find_element(
        *UfOPageLayout.REMOVE_ADMIN_FORM)
    admin_item = self.find_test_admin_on_remove_form(email, remove_admin_form)

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
