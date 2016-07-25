"""Test settings component and flows."""
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
from settings_component import SettingsComponent


class SettingsComponentTest(BaseTest):

  """Test settings component and flows.

  This could be part of the setup page tests, but is abstracted away for now
  in case we ever decide to make the settings component its own page or move
  it off of setup.
  """

  def setUp(self):
    """Setup for test methods."""
    super(SettingsComponentTest, self).setUp()
    super(SettingsComponentTest, self).set_context()
    LoginPage(self.driver).Login(self.args.server_url, self.args.email,
                                 self.args.password)
    settings_component = SettingsComponent(self.driver)
    self.driver.get(self.args.server_url)
    self.initial_settings = settings_component.getCurrentSettings()

  def tearDown(self):
    """Teardown for test methods."""
    settings_component = SettingsComponent(self.driver)
    self.driver.get(self.args.server_url)
    settings_component.resetSettings(self.initial_settings)
    LoginPage(self.driver).Logout(self.args.server_url)
    super(SettingsComponentTest, self).tearDown()

  def testSavingChangedSettings(self):
    """Test that changing a setting and saving it will actually retain it.

    Also tests that other settings are not changed when they shouldn't be.
    """
    proxy_server_key = 'enforce_proxy_server_validity'
    settings_component = SettingsComponent(self.driver)
    self.driver.get(self.args.server_url)
    settings_component.changeSetting(
        proxy_server_key, not self.initial_settings[proxy_server_key])

    # We specifically reload the page here to ensure that changes propagate to
    # the backend and are not solely in the UI.
    self.driver.get(self.args.server_url)
    changed_settings = settings_component.getCurrentSettings()

    for key, value in self.initial_settings.iteritems():
      self.assertIn(key, changed_settings)
      if key == proxy_server_key:
        self.assertNotEquals(self.initial_settings[key], changed_settings[key])
      else :
        self.assertEquals(self.initial_settings[key], changed_settings[key])

if __name__ == '__main__':
  unittest.main()
