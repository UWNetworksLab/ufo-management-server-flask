"""Test langing page module functionality."""
import unittest

from base_test import BaseTest
from landing_page import LandingPage
from test_config import CHROME_DRIVER_LOCATION

from selenium import webdriver


class LandingPageTest(BaseTest):

  """Test landing page functionality."""

  def setUp(self):
    """Setup for test methods."""
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    # TODO(eholder) Re-enable this once we have a login module again.
    # LoginPage(self.driver).Login(self.args)

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
    self.assertEquals(title, landing_page.GetTitle().text)
    self.assertEquals(instruction, landing_page.GetInstruction().text)
    self.assertIsNotNone(landing_page.GetSidebar())

  def tearDown(self):
    """Teardown for test methods."""
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
