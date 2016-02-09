"""Test langing page module functionality."""
import unittest

from base_test import BaseTest
from landing_page import LandingPage


class LandingPageTest(BaseTest):

  """Test landing page functionality."""

  def testLandingPage(self):
    """Test the landing page."""
    # TODO(eholder): Improve the checks here to be based on something more
    # robust, such as the presence of element id's or that the page renders
    # as expected, since this text can change in the future and is not i18ned.
    title = u'Uproxy for Organizations Management Server'
    instruction = ('Click one of the links on the side to login and '
                   'administer the server.')

    self.driver.get(self.args.server_url)

    landing_page = LandingPage(self.driver)
    title_elem = landing_page.GetElement(landing_page.TITLE)
    instruction_elem = landing_page.GetElement(landing_page.INSTRUCTION)
    self.assertEquals(title, title_elem.text)
    self.assertEquals(instruction, instruction_elem.text)
    self.assertIsNotNone(landing_page.GetSidebar())


if __name__ == '__main__':
  unittest.main()
