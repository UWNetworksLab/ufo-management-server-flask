"""Add and edit server form component for testing."""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from layout import UfOPageLayout

class ServerForm(UfOPageLayout):

  """Add and edit server form methods."""

  def addServer(self, containing_element, ip, name, private_key, public_key):
    """Add a test server using the element container to find the add form.

    Args:
      containing_element: An element containing the add server form.
      ip: A string for the ip address of the server to add.
      name: A string for the name of the server to add.
      private_key: A string for the private key of the server to add.
      public_key: A string for the public key of the server to add.
    """
    add_server_form = containing_element.find_element(
        *UfOPageLayout.ADD_SERVER_FORM)

    self._sendServerInputsToForm(add_server_form, ip, name, private_key,
                                 public_key, True)

    submit_button = self.driver.find_element(
        *UfOPageLayout.ADD_SERVER_SUBMIT_BUTTON)
    submit_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.ADD_SERVER_SPINNER))))

  def editServer(self, containing_element, ip, name, private_key, public_key):
    """Edit a test server using the element container to find the edit form.

    Args:
      containing_element: An element containing the edit server form.
      ip: A string for the ip address of the server to insert.
      name: A string for the name of the server to insert.
      private_key: A string for the private key of the server to insert.
      public_key: A string for the public key of the server to insert.
    """
    edit_server_form = containing_element.find_element(
        *UfOPageLayout.EDIT_SERVER_FORM)

    self._sendServerInputsToForm(edit_server_form, ip, name, private_key,
                                 public_key, False)

    submit_button = containing_element.find_element(
        *UfOPageLayout.EDIT_SERVER_SUBMIT_BUTTON)
    submit_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(containing_element, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.SERVER_DETAILS_SPINNER))))

  def _sendServerInputsToForm(self, form_element, ip, name, private_key,
                              public_key, is_add):
    """Send the necessary inputs to the form element.

    Args:
      form_element: A form element for adding or editing a server.
      ip: A string for the ip address of the server.
      name: A string for the name of the server.
      private_key: A string for the private key of the server.
      public_key: A string for the public key of the server.
      is_add: A boolean value, true for add flow or false for edit flow.
    """
    ip_paper_input = form_element.find_element(
        *UfOPageLayout.SERVER_INPUT_IP)
    ip_input = ip_paper_input.find_element(By.ID, 'input')
    self._cleanInputIfNecessary(ip_input, is_add)
    ip_input.send_keys(ip)

    name_paper_input = form_element.find_element(
        *UfOPageLayout.SERVER_INPUT_NAME)
    name_input = name_paper_input.find_element(By.ID, 'input')
    self._cleanInputIfNecessary(name_input, is_add)
    name_input.send_keys(name)

    private_key_paper_input = form_element.find_element(
        *UfOPageLayout.SERVER_INPUT_SSH_PRIVATE_KEY)
    private_key_input = None
    if is_add:
      private_key_input = private_key_paper_input.find_element(By.ID,
                                                               'textarea')
    else:
      private_key_input = private_key_paper_input.find_element(By.ID, 'input')
      self._cleanInputIfNecessary(private_key_input, is_add)
    private_key_input.send_keys(private_key)

    public_key_paper_input = form_element.find_element(
        *UfOPageLayout.SERVER_INPUT_HOST_PUBLIC_KEY)
    public_key_input = public_key_paper_input.find_element(By.ID, 'input')
    self._cleanInputIfNecessary(public_key_input, is_add)
    public_key_input.send_keys(public_key)

  def _cleanInputIfNecessary(self, input_element, is_add):
    """If necessary, remove the existing text in the input element.

    Args:
      input_element: An input element possibly with existing text.
      is_add: A boolean value, true for add flow or false for edit flow.
    """
    if not is_add:
      existing_input_text = input_element.get_attribute('value')
      for x in range(len(existing_input_text)):
        input_element.send_keys(Keys.BACKSPACE)
