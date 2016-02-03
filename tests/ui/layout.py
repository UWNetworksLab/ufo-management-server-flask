"""Layout module to abstract away the sidebar and future common elements."""

from selenium.webdriver.common.by import By

from base_driver import BaseDriver
from sidebar import Sidebar

class UfOPageLayout(BaseDriver):

  """Page layout class with a sidebar and to hold future common elements."""

  # pylint: disable=too-few-public-methods

  def GetSidebar(self):
    """Get the sidebar element on the user page.

    Returns:
      The sidebar element for any page.
    """
    return self.driver.find_element(*Sidebar.SIDEBAR)
