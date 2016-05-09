"""Test runner for functional testing."""
import argparse
import unittest

from admin_flow_test import AdminFlowTest
from error_notification_test import ErrorNotificationTest
from landing_page_test import LandingPageTest
from login_page_test import LoginPageTest
from search_page_test import SearchPageTest
from settings_component_test import SettingsComponentTest
from setup_page_test import SetupPageTest
from undefined_url_test import UndefinedURLTest


def _ParseArgs():
  """Parse the arguments from the commandline.

    Returns:
      The parsed arguments given from the command line as an args array.
    """
  parser = argparse.ArgumentParser()
  parser.add_argument('--server_url', action='store',
                      dest='server_url', default=None,
                      help='URL of the server to test.')
  parser.add_argument('--email', action='store',
                      dest='email', default=None,
                      help='Email of the user to login.')
  parser.add_argument('--password', action='store',
                      dest='password', default=None,
                      help='Password of the user to login.')
  return parser.parse_args()

def MakeSuite(testcase_class):
  """Add the test cases into suites.

    Args:
      testcase_class: The class of test case to make into a test suite.

    Returns:
      A test suite for the given case.
    """
  testloader = unittest.TestLoader()
  test_cases = testloader.getTestCaseNames(testcase_class)
  test_suite = unittest.TestSuite()
  for test_case in test_cases:
    test_suite.addTest(testcase_class(test_case, args=_ParseArgs()))
  return test_suite

SUITE = unittest.TestSuite()
SUITE.addTest(MakeSuite(AdminFlowTest))
SUITE.addTest(MakeSuite(ErrorNotificationTest))
SUITE.addTest(MakeSuite(LandingPageTest))
SUITE.addTest(MakeSuite(LoginPageTest))
SUITE.addTest(MakeSuite(SearchPageTest))
SUITE.addTest(MakeSuite(SettingsComponentTest))
SUITE.addTest(MakeSuite(SetupPageTest))
SUITE.addTest(MakeSuite(UndefinedURLTest))

unittest.TextTestRunner().run(SUITE)
