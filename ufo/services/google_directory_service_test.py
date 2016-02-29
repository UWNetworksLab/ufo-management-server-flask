"""Test google directory service module functionality."""
import json
import unittest

import flask
from googleapiclient import discovery
import mock

from ufo import base_test
# I practically have to shorten this name so every single line doesn't go
# over. If someone can't understand, they can use ctrl+f to look it up here.
from ufo.services import google_directory_service as gds


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
  """Create a mocked out google directory service.

  This is a helper method to facilitate testing the google directory service
  module by building an instance according to what we expect in testing. It
  mocks out calls to authorize on a fake set of credentials so that build in
  the __init__ function will pass correctly.

  Returns:
    A mock google directory service instance using mock_credentials.
  """
  def mock_authorize(http):
    """Mock authorize function to return None.

    Args:
      http: Unused argument which is here purely to meet the method signature.

    Returns:
      None
    """
    return None

  mock_credentials = mock.MagicMock()
  mock_credentials.authorize = mock_authorize
  directory_service = gds.GoogleDirectoryService(mock_credentials)
  return directory_service


class GoogleDirectoryServiceTest(base_test.BaseTest):
  """Test google directory service class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(GoogleDirectoryServiceTest, self).setUp()
    super(GoogleDirectoryServiceTest, self).setup_config()

  @mock.patch.object(discovery, 'build')
  def testGetUsers(self, mock_build):
    """Test get users request handles a multi-page response correctly.

    Args:
      mock_build: A mocked instance of discovery.build on which we create
                  subsequent mocks in order to drive fake responses from the
                  directory API.
    """
    fake_dictionary_1 = {
        'users': FAKE_USERS,
        'nextPageToken': FAKE_PAGE_TOKEN
    }
    fake_extra_user = mock.MagicMock()
    fake_dictionary_2 = {
        'users': [fake_extra_user]
    }
    expected_list = FAKE_USERS + [fake_extra_user]


    def _ReturnDomainUsersForPageToken(domain, maxResults, pageToken,
                                       projection, orderBy):
      """Mock list function to return different mock execute calls.

      Args:
        domain: Unused argument which is purely here to meet the list method
                signature.
        maxResults: Unused argument which is purely here to meet the list
                    method signature.
        pageToken: A string token representing which page of a long list of
                   data should be returned for a given request. We use this to
                   determine which dictionary of users to return from mock
                   execute.
        projection: Unused argument which is purely here to meet the list
                    method signature.
        orderBy: Unused argument which is purely here to meet the list method
                 signature.

      Returns:
        A dictionary of directory service users for the corresponding page
        token.
      """
      # pylint: disable=unused-argument
      mock_execute = mock.MagicMock()
      if pageToken == '':
        mock_execute.execute.return_value = fake_dictionary_1
      else:
        mock_execute.execute.return_value = fake_dictionary_2
      return mock_execute

    # This weird looking structure is to mock out a call buried behind several
    # objects which requires going through the method's return_value for each
    # method down the chain, starting from the discovery module.
    users_object = mock_build.return_value.users.return_value
    users_object.list.side_effect = _ReturnDomainUsersForPageToken

    directory_service = make_mock_directory_service()
    users_returned = directory_service.GetUsers()

    self.assertEqual(users_returned, expected_list)

  @mock.patch.object(gds.GoogleDirectoryService, 'GetUser')
  @mock.patch.object(discovery, 'build')
  def testGetUsersByGroupKey(self, mock_build, mock_get_user):
    """Test get users by group key handles a multi-page response correctly.

    Args:
      mock_build: A mocked instance of discovery.build on which we create
                  subsequent mocks in order to drive fake responses from the
                  directory API.
      mock_get_user: A mocked get user function so we can return fake directory
                     user dictionaries upon a lookup from a group.
    """
    fake_dictionary_1 = {
        'members': FAKE_GROUP,
        'nextPageToken': FAKE_PAGE_TOKEN
    }
    fake_dictionary_2 = {
        'members': FAKE_GROUP
    }
    expected_list = [FAKE_GROUP_MEMBER_USER_1, FAKE_GROUP_MEMBER_USER_2,
                     FAKE_GROUP_MEMBER_USER_1, FAKE_GROUP_MEMBER_USER_2]


    def _ReturnGroupsForPageToken(groupKey, pageToken=''):
      """Mock list function to return different mock execute calls.

      Args:
        groupKey: Unused argument which is purely here to meet the list method
                  signature.
        pageToken: A string token representing which page of a long list of
                   data should be returned for a given request. We use this to
                   determine which dictionary of group members to return from
                   mock execute.

      Returns:
        A dictionary of directory service group members for the corresponding
        page token.
      """
      # pylint: disable=unused-argument
      mock_execute = mock.MagicMock()
      if pageToken == '':
        mock_execute.execute.return_value = fake_dictionary_1
      else:
        mock_execute.execute.return_value = fake_dictionary_2
      return mock_execute

    # This weird looking structure is to mock out a call buried behind several
    # objects which requires going through the method's return_value for each
    # method down the chain, starting from the discovery module.
    members_object = mock_build.return_value.members.return_value
    members_object.list.side_effect = _ReturnGroupsForPageToken

    def _ReturnGroupMembersForUserKey(user_key):
      """Mock get user function to return different users after group get.

      Args:
        user_key: The key identifying a requested user. Used to determine
                  which group member should be returned.

      Returns:
        A group member which is a user corresponding to a given user key.
      """
      if user_key == FAKE_ID_1:
        return FAKE_GROUP_MEMBER_USER_1
      else:
        return FAKE_GROUP_MEMBER_USER_2

    mock_get_user.side_effect = _ReturnGroupMembersForUserKey

    directory_service = make_mock_directory_service()
    users_returned = directory_service.GetUsersByGroupKey(FAKE_GROUP_KEY)

    self.assertEqual(users_returned, expected_list)


if __name__ == '__main__':
  unittest.main()
