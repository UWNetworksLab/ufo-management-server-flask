"""Test setup page module functionality."""
import unittest

from base_test import BaseTest
from setup_page import SetupPage

import flask
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class SetupPageTest(BaseTest):

  """Test setup page functionality."""

  def setUp(self):
    """Setup for test methods."""
    super(SetupPageTest, self).setUp()
    super(SetupPageTest, self).setContext()

    # TODO(eholder): Fill this in with some tests for the setup page flows.

  def tearDown(self):
    """Teardown for test methods."""
    super(SetupPageTest, self).tearDown()


if __name__ == '__main__':
  unittest.main()
