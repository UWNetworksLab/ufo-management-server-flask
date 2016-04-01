"""Settings component for testing."""

import flask
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from layout import UfOPageLayout

class SettingsComponent(UfOPageLayout):

  """Settings component methods."""

  def __init__(self, driver):
    """Create the base driver object.

    Args:
      driver: A webdriver instance that can be used to query the dom.
    """
    super(UfOPageLayout, self).__init__(driver)
    self.setting_url = (flask.url_for('setup') + '#' +
                        self.SETTINGS_DISPLAY_TEMPLATE_ID)

  def getCurrentSettings(self):
    """Find the current settings on the page and return them.

    This specifically excludes the xsrf token since it isn't necessary for
    testing here as well as any future paper-inputs which might be mirrored to
    standard input elements, as denoted by the paper-input's name starting with
    'paper'.

    Returns:
      A dictionary containing each of the current settings' name and value.
    """
    settings_holder = self.driver.find_element(*self.SETTINGS_DISPLAY_TEMPLATE)
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

  def resetSettings(self, initial_settings):
    """Reset all of the settings back to their given, initial values.

    Args:
      initial_settings: A dictionary of settings and values to reset the
                        setting back to.
    """
    # Sanity check that each setting exists and does not match already.
    current_settings = self.getCurrentSettings()
    for key, value in initial_settings.iteritems():
      if key not in current_settings:
        continue
      if current_settings[key] == value:
        continue
      self.changeSetting(key, value, should_save=False)

    self.saveSettings()

  def changeSetting(self, setting_key, new_setting_value, should_save=True):
    """Find the given setting and change it to the value specified.

    Args:
      setting_key: A string for the key of a setting in a settings dictionary.
      new_setting_value: The value to set the given setting to.
      should_save: True (default) to save after changing the setting. False to
                   not click save (useful for batching several changes then
                   clicking save after all have been changed).
    """
    # Sanity check that the setting exists and does not match already.
    current_settings = self.getCurrentSettings()
    if setting_key not in current_settings:
      return
    if current_settings[setting_key] == new_setting_value:
      return

    # TODO(eholder): Implement changers for other settings as necessary.
    if setting_key == 'enforce_proxy_server_validity':
      self._changeProxyServerSetting(setting_key)

    if should_save:
      self.saveSettings()

  def saveSettings(self):
    """Click the save button to save the current settings."""
    settings_holder = self.driver.find_element(*self.SETTINGS_DISPLAY_TEMPLATE)
    save_button = settings_holder.find_element(*self.SETTINGS_SAVE_BUTTON)
    save_button.click()

    # Wait for post to finish, can take a while.
    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((self.SETTINGS_SPINNER))))

  def _changeProxyServerSetting(self, setting_key):
    """Change the proxy server setting.

    Args:
      setting_key: A string for the key of a setting in a settings dictionary.
    """
    # Find the element to interact with and then perform the change.
    settings_holder = self.driver.find_element(*self.SETTINGS_DISPLAY_TEMPLATE)
    toggles =  settings_holder.find_elements(By.TAG_NAME, 'ufo-toggle-input')
    setting_to_change = None
    for toggle in toggles:
      name = toggle.get_attribute('input-name')
      if name == setting_key:
        toggle.click()
        break
