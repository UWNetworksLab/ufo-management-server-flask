"""Test google directory service module functionality."""
from mock import MagicMock
from mock import patch

import flask
from googleapiclient import discovery
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
FAKE_ID_1 = 'some id 1' # Also doubles as a user key
FAKE_ID_2 = 'some id 2'
FAKE_GROUP_MEMBER_USER_1 = {}
FAKE_GROUP_MEMBER_USER_1['type'] = 'USER'
FAKE_GROUP_MEMBER_USER_1['id'] = FAKE_ID_1
FAKE_GROUP_MEMBER_USER_2 = {}
FAKE_GROUP_MEMBER_USER_2['type'] = 'USER'
FAKE_GROUP_MEMBER_USER_2['id'] = FAKE_ID_2
FAKE_GROUP_MEMBER_GROUP = {}
FAKE_GROUP_MEMBER_GROUP['type'] = 'GROUP'
FAKE_GROUP = [FAKE_GROUP_MEMBER_USER_1, FAKE_GROUP_MEMBER_USER_2,
              FAKE_GROUP_MEMBER_GROUP]
FAKE_PAGE_TOKEN = 'I am a fake page token.'
FAKE_GROUP_KEY = "my_group@mybusiness.com"


def make_mock_directory_service():
  """Create a mocked out google directory service."""
  def mock_authorize(http):
    """Mock authorize function to return None."""
    return None

  mock_credentials = MagicMock()
  mock_credentials.authorize = mock_authorize
  directory_service = gds.GoogleDirectoryService(mock_credentials)
  return directory_service


class GoogleDirectoryServiceTest(base_test.BaseTest):
  """Test google directory service class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(GoogleDirectoryServiceTest, self).setUp()
    super(GoogleDirectoryServiceTest, self).setup_config()

  @patch.object(discovery, 'build')
  def testGetUsers(self, mock_build):
    """Test get users request handles a valid response correctly."""
    fake_dictionary = {}
    fake_dictionary['users'] = FAKE_USERS
    # This weird looking structure is to mock out a call buried behind several
    # objects which requires going through the method's return_value for each
    # method down the chain, starting from the discovery module.
    users_object = mock_build.return_value.users.return_value
    list_object = users_object.list.return_value
    list_object.execute.return_value = fake_dictionary

    directory_service = make_mock_directory_service()
    users_returned = directory_service.GetUsers()

    self.assertEqual(users_returned, FAKE_USERS)

  @patch.object(gds.GoogleDirectoryService, 'GetUser')
  @patch.object(discovery, 'build')
  def testGetUsersByGroupKey(self, mock_build, mock_get_user):
    """Test get users by group key handles a valid response correctly."""
    fake_dictionary = {}
    fake_dictionary['members'] = FAKE_GROUP
    expected_list = [FAKE_GROUP_MEMBER_USER_1, FAKE_GROUP_MEMBER_USER_2]
    # This weird looking structure is to mock out a call buried behind several
    # objects which requires going through the method's return_value for each
    # method down the chain, starting from the discovery module.
    members_object = mock_build.return_value.members.return_value
    list_object = members_object.list.return_value
    list_object.execute.return_value = fake_dictionary

    def SideEffect(user_key):
      """Mock get user function to return different users after group get."""
      if user_key == FAKE_ID_1:
        return FAKE_GROUP_MEMBER_USER_1
      else:
        return FAKE_GROUP_MEMBER_USER_2

    mock_get_user.side_effect = SideEffect

    directory_service = make_mock_directory_service()
    users_returned = directory_service.GetUsersByGroupKey(FAKE_GROUP_KEY)

    self.assertEqual(users_returned, expected_list)


if __name__ == '__main__':
  unittest.main()
