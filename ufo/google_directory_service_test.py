"""Test google directory service module functionality."""
from mock import MagicMock
from mock import patch

import flask
from googleapiclient import http
import json
import unittest

import base_test
# I practically have to shorten this name so every single line doesn't go
# over. If someone can't understand, they can use ctrl+f to look it up here.
import google_directory_service as gds


FAKE_EMAIL_1 = 'foo@mybusiness.com'
FAKE_EMAIL_2 = 'bar@mybusiness.com'
FAKE_USER_1 = {}
FAKE_USER_1['primaryEmail'] = FAKE_EMAIL_1
FAKE_USER_1['isAdmin'] = True
FAKE_USER_2 = {}
FAKE_USER_2['primaryEmail'] = FAKE_EMAIL_2
FAKE_USER_2['isAdmin'] = False
FAKE_USERS = [FAKE_USER_1, FAKE_USER_2]


def make_mock_directory_service(http_mock):
  """Create a mocked out google directory service with the http mock passed."""
  # Setting up mocks for the service based on the example shown here:
  # https://developers.google.com/api-client-library/python/guide/mocks
  # def mock_authorize(http):
  #   """Mock authorize function to return a mocked object."""
  #   return http_mock

  # mock_credentials = MagicMock()
  # mock_credentials.authorize = mock_authorize
  directory_service = gds.GoogleDirectoryService(None, http=http_mock)
  return directory_service


class GoogleDirectoryServiceTest(base_test.BaseTest):
  """Test google directory service class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(GoogleDirectoryServiceTest, self).setUp()
    super(GoogleDirectoryServiceTest, self).setup_config()

  def testGetUsers(self):
    """Test the get users request handles a valid response correctly."""
    fake_dictionary = {}
    fake_dictionary['users'] = FAKE_USERS
    json_dictionary = json.dumps(fake_dictionary)
    http_mock = http.HttpMockSequence([({'status': '200'}, json_dictionary)])
    directory_service = make_mock_directory_service(http_mock)

    users_returned = directory_service.GetUsers()

    self.assertEqual(users_returned, FAKE_USERS)


if __name__ == '__main__':
  unittest.main()
