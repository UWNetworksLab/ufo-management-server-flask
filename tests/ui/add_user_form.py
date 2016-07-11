"""Add user form component for testing."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from layout import UfOPageLayout

class AddUserForm(UfOPageLayout):

  """Add user form methods."""

  # pylint: disable=too-few-public-methods

  def add_test_user(self, name, email):
    """Manually add a test user from the form.

    Args:
      name: A string for the name of a test user.
      email: A string for the email of a test user.
    """
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((UfOPageLayout.ADD_MANUALLY_FORM))))
    add_manually_form = self.driver.find_element(
        *UfOPageLayout.ADD_MANUALLY_FORM)
    name_paper_input = add_manually_form.find_element(
        *UfOPageLayout.ADD_MANUALLY_INPUT_NAME)
    name_input = name_paper_input.find_element(By.ID, 'input')
    name_input.send_keys(name)
    email_paper_input = add_manually_form.find_element(
        *UfOPageLayout.ADD_MANUALLY_INPUT_EMAIL)
    email_input = email_paper_input.find_element(By.ID, 'input')
    email_input.send_keys(email)
    submit_button = self.driver.find_element(
        *UfOPageLayout.ADD_MANUALLY_SUBMIT_BUTTON)
    submit_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.ADD_MANUALLY_SPINNER))))
