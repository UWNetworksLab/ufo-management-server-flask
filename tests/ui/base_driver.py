"""Base driver module to inherit from."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class BaseDriver(object):

  """Base driver that will be called from all pages and elements."""

  GENERIC_DIV = (By.TAG_NAME, 'div')
  DEFAULT_TIMEOUT = 30

  def __init__(self, driver):
    """Create the base driver object.

    Args:
      driver: A webdriver instance that can be used to query the dom.
    """
    self.driver = driver


  def GetLink(self, link_locator):
    """Get an element in the page based on the link locator given.

    Args:
      link_locator: A tuple of By.SomeProperty and a matching property.

    Returns:
      A link element if found.
    """
    return WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((link_locator))))

  def GetElement(self, element_locator):
    """Get an element in the page based on the element locator given.

    Args:
      element_locator: A tuple of By.SomeProperty and a matching property.

    Returns:
      A generic element if found.
    """
    return self.driver.find_element(*element_locator)
