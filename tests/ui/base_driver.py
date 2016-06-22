"""Base driver module to inherit from."""

from selenium.webdriver.common.by import By

class BaseDriver(object):

  """Base driver that will be called from all pages and elements."""

  # pylint: disable=too-few-public-methods

  GENERIC_DIV = (By.TAG_NAME, 'div')
  DEFAULT_TIMEOUT = 30

  def __init__(self, driver):
    """Create the base driver object.

    Args:
      driver: A webdriver instance that can be used to query the dom.
    """
    self.driver = driver

  def get_element(self, element_locator):
    """Get an element in the page based on the element locator given.

    Args:
      element_locator: A tuple of By.SomeProperty and a matching property.

    Returns:
      A generic element if found.
    """
    return self.driver.find_element(*element_locator)
