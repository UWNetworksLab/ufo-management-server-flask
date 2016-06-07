"""Setup page module functionality for getting elements for testing."""

import flask

from server_form import ServerForm
from add_user_form import AddUserForm
from layout import UfOPageLayout
from settings_component import SettingsComponent


class SetupPage(UfOPageLayout):

  """Setup page action methods and locators."""

  SETUP_PAGE_ELEMENTS = [
    UfOPageLayout.USER_DISPLAY_TEMPLATE,
    UfOPageLayout.PROXY_SERVER_DISPLAY_TEMPLATE,
    UfOPageLayout.OAUTH_DISPLAY_TEMPLATE,
    UfOPageLayout.CHROME_POLICY_DISPLAY_TEMPLATE,
    SettingsComponent.SETTINGS_DISPLAY_TEMPLATE
  ]

  def addTestUser(self, name, email, server_url):
    """Manually add a test user using the setup page.

    Args:
      name: A string for the name of a test user.
      email: A string for the email of a test user.
      server_url: The base url portion of the setup page.
    """
    # Navigate to add user and go to manual tab.
    self.driver.get(server_url + flask.url_for('setup'))
    add_manually_tab = self.GetElement(UfOPageLayout.ADD_MANUALLY_TAB)
    add_manually_tab.click()

    add_user_form = AddUserForm(self.driver)
    add_user_form.addTestUser(name, email)

  def addTestServer(self, ip, name, ssh_private_key, host_public_key,
                    server_url):
    """Add a test server using the setup page.

    Args:
      ip: A string for the ip address of the server to add.
      name: A string for the name of the server to add.
      ssh_private_key: A string for the ssh private key of the server to add.
      host_public_key: A string for the host public key of the server to add.
      server_url: The base url portion of the setup page.
    """
    # Navigate to add server.
    self.driver.get(server_url + flask.url_for('setup'))
    proxy_server_add_template = self.GetElement(
        UfOPageLayout.PROXY_SERVER_DISPLAY_TEMPLATE)

    server_form = ServerForm(self.driver)
    server_form.addServer(proxy_server_add_template, ip, name, ssh_private_key,
                          host_public_key)

