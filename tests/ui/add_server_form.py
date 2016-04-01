"""Add server form component for testing."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from layout import UfOPageLayout

class AddServerForm(UfOPageLayout):

  """Add server form methods."""

  # pylint: disable=too-few-public-methods

  def addTestServer(self, containing_element, ip, name, private_key,
                    public_key):
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

    ip_paper_input = add_server_form.find_element(
        *UfOPageLayout.ADD_SERVER_INPUT_IP)
    ip_input = ip_paper_input.find_element(By.ID, 'input')
    ip_input.send_keys(ip)

    name_paper_input = add_server_form.find_element(
        *UfOPageLayout.ADD_SERVER_INPUT_NAME)
    name_input = name_paper_input.find_element(By.ID, 'input')
    name_input.send_keys(name)

    private_key_paper_input = add_server_form.find_element(
        *UfOPageLayout.ADD_SERVER_INPUT_PRIVATE_KEY)
    private_key_input = private_key_paper_input.find_element(By.ID, 'textarea')
    private_key_input.send_keys(private_key)

    public_key_paper_input = add_server_form.find_element(
        *UfOPageLayout.ADD_SERVER_INPUT_PUBLIC_KEY)
    public_key_input = public_key_paper_input.find_element(By.ID, 'input')
    public_key_input.send_keys(public_key)

    submit_button = self.driver.find_element(
        *UfOPageLayout.ADD_SERVER_SUBMIT_BUTTON)
    submit_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, UfOPageLayout.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.ADD_SERVER_SPINNER))))
