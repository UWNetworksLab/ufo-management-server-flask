"""Settings component for testing."""

import flask
from selenium.webdriver.common.by import By

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
