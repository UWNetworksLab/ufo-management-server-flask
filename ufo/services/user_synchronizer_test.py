"""Test user synchronizer module functionality."""

import json

import logging
from mock import patch

import ufo
from ufo import base_test
from ufo.database import models
from ufo.services import google_directory_service as gds
from ufo.services import oauth
from ufo.services import user_synchronizer


class UserSynchronizerTest(base_test.BaseTest):
  """Test UserSynchronizer class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(UserSynchronizerTest, self).setUp()
    super(UserSynchronizerTest, self).setup_config()
    # Turning down the logging since user sync can spit out a lot of messages.
    ufo.app.logger.setLevel(logging.ERROR)

  @patch.object(gds.GoogleDirectoryService, 'GetUsersAsDictionary')
  @patch.object(gds.GoogleDirectoryService, '__init__')
  @patch.object(oauth, 'getSavedCredentials')
  def testUsersInNonMatchingDomainLeftUnchanged(self, mock_get_credentials,
                                                mock_gds, mock_get_users):
    """Test that users not matching the current domain are ignored.

    Args:
      mock_get_credentials: A mocked oauth.getSavedCredentials call.
      mock_gds: A mocked gds.init call so that it doesn't fail.
      mock_get_users: A mocked gds.GetUsersAsDictionary call which we spoof.
    """
    mock_get_credentials.return_value = 'foo'
    mock_gds.return_value = None
    mock_get_users.return_value = {}
    self.create_user_with_manual_post()

    initial_db_users = models.User.get_items_as_list_of_dict()

    syncer = user_synchronizer.UserSynchronizer()
    syncer.sync_db_users_against_directory_service()

    final_db_users = models.User.get_items_as_list_of_dict()

    for initial_db_user in initial_db_users:
      self.assertIn(initial_db_user, final_db_users)

  @patch.object(gds.GoogleDirectoryService, 'GetUsersAsDictionary')
  @patch.object(gds.GoogleDirectoryService, '__init__')
  @patch.object(oauth, 'getSavedCredentials')
  def testUsersNotFoundInDirectoryAreDeleted(self, mock_get_credentials,
                                             mock_gds, mock_get_users):
    """Test users not found but matching the current domain are deleted.

    Args:
      mock_get_credentials: A mocked oauth.getSavedCredentials call.
      mock_gds: A mocked gds.init call so that it doesn't fail.
      mock_get_users: A mocked gds.GetUsersAsDictionary call which we spoof.
    """
    mock_get_credentials.return_value = 'foo'
    mock_gds.return_value = None
    mock_get_users.return_value = {}
    self.create_users_with_google_directory_service_post()
    # I could explicitly set the config to delete here, but it is on by
    # default, so that is assumed.

    initial_db_users = models.User.get_items_as_list_of_dict()

    syncer = user_synchronizer.UserSynchronizer()
    syncer.sync_db_users_against_directory_service()

    final_db_users = models.User.get_items_as_list_of_dict()

    for initial_db_user in initial_db_users:
      self.assertNotIn(initial_db_user, final_db_users)

  @patch.object(gds.GoogleDirectoryService, 'GetUsersAsDictionary')
  @patch.object(gds.GoogleDirectoryService, '__init__')
  @patch.object(oauth, 'getSavedCredentials')
  def testSuspendedUsersAreRevoked(self, mock_get_credentials, mock_gds,
                                   mock_get_users):
    """Test users suspended in gds but matching the current domain are revoked.

    Args:
      mock_get_credentials: A mocked oauth.getSavedCredentials call.
      mock_gds: A mocked gds.init call so that it doesn't fail.
      mock_get_users: A mocked gds.GetUsersAsDictionary call which we spoof.
    """
    mock_get_credentials.return_value = 'foo'
    mock_gds.return_value = None
    mock_users = {}
    for fake_email_and_name in base_test.FAKE_EMAILS_AND_NAMES:
      mock_user = { 'suspended': True }
      mock_users[fake_email_and_name['email']] = mock_user
    mock_get_users.return_value = mock_users
    self.create_users_with_google_directory_service_post()
    # I could explicitly set the config to revoke here, but it is on by
    # default, so that is assumed.

    initial_db_users = models.User.query.all()
    for initial_db_user in initial_db_users:
      self.assertEquals(False, initial_db_user.is_key_revoked)
      self.assertEquals(False, initial_db_user.did_cron_revoke)

    syncer = user_synchronizer.UserSynchronizer()
    syncer.sync_db_users_against_directory_service()

    final_db_users = models.User.query.all()
    for final_db_user in final_db_users:
      self.assertEquals(True, final_db_user.is_key_revoked)
      self.assertEquals(True, final_db_user.did_cron_revoke)


if __name__ == '__main__':
  unittest.main()
