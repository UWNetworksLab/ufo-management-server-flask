"""Test settings flows."""
import unittest

import flask
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base_test import BaseTest
from login_page import LoginPage
from layout import UfOPageLayout


class SettingsFlowTest(BaseTest):

  """Test settings flows.

  This could be part of the setup page tests, but is abstracted away for now
  in case we ever decide to make the settings component its own page or move
  it off of setup.
  """

  def setUp(self):
    """Setup for test methods."""
    super(SettingsFlowTest, self).setUp()
    super(SettingsFlowTest, self).setContext()
    LoginPage(self.driver).Login(self.args.server_url, self.args.username,
                                 self.args.password)
    self.handlers = [
      flask.url_for('landing'),
      flask.url_for('setup'),
      flask.url_for('search_page', search_text='"foo"')
    ]
    self.setting_url = (self.args.server_url + flask.url_for('setup') + '#' +
                        UfOPageLayout.SETTINGS_DISPLAY_TEMPLATE_ID)
    self.driver.get(self.setting_url)
    self.initial_settings = self._getCurrentSettings()

  def tearDown(self):
    """Teardown for test methods."""
    # self._resetServerSettings()
    LoginPage(self.driver).Logout(self.args.server_url)
    super(SettingsFlowTest, self).tearDown()

  def testAllPagesHaveLinkToSettings(self):
    """Test that each page has a link in the dropdown to navigate to settings."""
    for handler in self.handlers:
      self._assertLinkToSettingsIsPresent(self.args.server_url + handler)

  # def testSavingChangedSettings(self):
  #   """Test that changing a setting and saving it will actually retain it.

  #   Also tests that other settings are not changed when they shouldn't be.
  #   """
  #   self.driver.get(self.setting_url)
  #   self._changeSetting('enforce_proxy_server_validity')

  #   self.driver.get(self.setting_url)
  #   changed_settings = self._getCurrentSettings()

  #   for (key, value) in self.initial_settings:
  #     self.assertIn(key, changed_settings)
  #     if key == 'enforce_proxy_server_validity':
  #       self.assertNotEquals(self.initial_settings[key], changed_settings[key])
  #     else :
  #       self.assertEquals(self.initial_settings[key], changed_settings[key])

  def _assertLinkToSettingsIsPresent(self, test_url):
    """Assert that the link to the settings page is present on the given url.

    Args:
      test_url: The url to navigate to and assert based upon.
    """
    self.driver.get(test_url)
    dropdown_menu = self.getDropdownMenu()
    settings_link = dropdown_menu.find_element(*UfOPageLayout.SETTINGS_ANCHOR)
    self.assertEquals(self.setting_url, settings_link.get_attribute('href'))

  def _getCurrentSettings(self):
    """Find the current settings on the page and return them.

    This specifically excludes the xsrf token since it isn't necessary for
    testing here as well as any future paper-inputs which might be mirrored to
    standard input elements, as denoted by the paper-input's name starting with
    'paper'.

    Returns:
      A dictionary containing each of the current settings' name and value.
    """
    settings_holder = self.driver.find_element(
        *UfOPageLayout.SETTINGS_DISPLAY_TEMPLATE)
    input_elements =  settings_holder.find_elements(By.TAG_NAME, 'input')
    settings_dictionary = {}
    for input_element in input_elements:
      name = input_element.get_attribute('name')
      if name == '_xsrf_token':
        continue
      elif name.startswith('paper'):
        continue
      value = input_element.get_attribute('value')
      settings_dictionary[name] = value
    return settings_dictionary


if __name__ == '__main__':
  unittest.main()
