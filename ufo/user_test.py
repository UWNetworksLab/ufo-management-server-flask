"""Test user module functionality."""
from mock import MagicMock
from mock import patch
import os

import flask
from flask.ext.testing import TestCase
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import unittest

from . import app
from . import db
from . import models
from . import user

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

FAKE_EMAILS_AND_NAMES = [
  {'email': 'foo@aol.com', 'name': 'joe'},
  {'email': 'bar@yahoo.com', 'name': 'bob'},
  {'email': 'baz@gmail.com', 'name': 'mark'}
]

class UserTest(TestCase):

  """Test user class functionality."""

  def create_app(self):
    app.config.from_object('config.TestConfiguration')
    return app

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    db.create_all()

    self.config = models.Config()
    self.config.isConfigured = True
    self.config.id = 0

    self.config.Add()

  def tearDown(self):
    """Teardown the test db and instances."""
    db.session.delete(self.config)
    db.session.commit()
    db.session.close()

  @patch.object(models.User, 'GetAll')
  def testListUsersHandler(self, mock_get_all):
    """Test the list user handler displays users from the database."""
    mock_users = []
    for x in range(0, len(FAKE_EMAILS_AND_NAMES)):
      mock_user = MagicMock(id=x + 1, email=FAKE_EMAILS_AND_NAMES[x]['email'],
                            name=FAKE_EMAILS_AND_NAMES[x]['name'])
      mock_users.append(mock_user)
    mock_get_all.return_value = mock_users

    resp = self.client.get(flask.url_for('user_list'))
    user_list_output = resp.data

    self.assertEquals('Add Users' in user_list_output, True)
    click_user_string = 'Click a user below to view more details.'
    self.assertEquals(click_user_string in user_list_output, True)

    for x in range(0, len(FAKE_EMAILS_AND_NAMES)):
      self.assertEquals(FAKE_EMAILS_AND_NAMES[x]['email'] in user_list_output,
                        True)
      details_link = flask.url_for('user_details', user_id=mock_users[x].id)
      self.assertEquals(details_link in user_list_output, True)

  @patch.object(user, '_RenderUserAdd')
  def testAddUsersGetHandler(self, mock_render):
    """Test the add users get handler returns _RenderUserAdd's result."""
    return_text = '<html>something here </html>'
    mock_render.return_value = return_text
    resp = self.client.get(flask.url_for('add_user'))

    self.assertEquals(resp.data, return_text)

  # @patch('user.User.InsertUsers')
  # def testAddUsersPostHandler(self, mock_insert):
  #   """Test the add users post handler calls to insert the specified users."""
  #   user_1 = {}
  #   user_1['primaryEmail'] = FAKE_EMAIL_1
  #   user_1['name'] = {}
  #   user_1['name']['fullName'] = FAKE_EMAIL_1
  #   user_2 = {}
  #   user_2['primaryEmail'] = FAKE_EMAIL_2
  #   user_2['name'] = {}
  #   user_2['name']['fullName'] = FAKE_EMAIL_2
  #   user_array = []
  #   user_array.append(user_1)
  #   user_array.append(user_2)
  #   data = '?selected_user={0}&selected_user={1}'.format(user_1, user_2)
  #   response = self.testapp.post(PATHS['user_add_path'] + data)

  #   mock_insert.assert_called_once_with(user_array)
  #   self.assertEqual(response.status_int, 302)
  #   self.assertTrue(PATHS['user_page_path'] in response.location)

  # @patch('user.User.InsertUsers')
  # def testAddUsersPostManualHandler(self, mock_insert):
  #   """Test add users manually calls to insert the specified user."""
  #   user_1 = {}
  #   user_1['primaryEmail'] = FAKE_EMAIL
  #   user_1['name'] = {}
  #   user_1['name']['fullName'] = FAKE_NAME
  #   user_array = []
  #   user_array.append(user_1)
  #   data = '?manual=true&user_name={0}&user_email={1}'.format(FAKE_NAME,
  #                                                             FAKE_EMAIL)
  #   response = self.testapp.post(PATHS['user_add_path'] + data)

  #   mock_insert.assert_called_once_with(user_array)
  #   self.assertEqual(response.status_int, 302)
  #   self.assertTrue(PATHS['user_page_path'] in response.location)

  # @patch('user._RenderAddUsersTemplate')
  # @patch('google_directory_service.GoogleDirectoryService.WatchUsers')
  # @patch('google_directory_service.GoogleDirectoryService.GetUserAsList')
  # @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  # @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  # @patch('google_directory_service.GoogleDirectoryService.__init__')
  # def testAddUsersGetHandlerNoParam(self, mock_ds, mock_get_users,
  #                                   mock_get_by_key, mock_get_user,
  #                                   mock_watch_users, mock_render):
  #   """Test the add users get handler displays no users on initial get."""
  #   # pylint: disable=too-many-arguments
  #   mock_ds.return_value = None
  #   self.testapp.get(PATHS['user_add_path'])

  #   mock_ds.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
  #   mock_get_users.assert_not_called()
  #   mock_get_user.assert_not_called()
  #   mock_get_by_key.assert_not_called()
  #   mock_watch_users.assert_not_called()
  #   mock_render.assert_called_once_with([])

  # @patch('user._RenderAddUsersTemplate')
  # @patch('google_directory_service.GoogleDirectoryService.WatchUsers')
  # @patch('google_directory_service.GoogleDirectoryService.GetUserAsList')
  # @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  # @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  # @patch('google_directory_service.GoogleDirectoryService.__init__')
  # def testAddUsersGetHandlerWithGroup(self, mock_ds, mock_get_users,
  #                                     mock_get_by_key, mock_get_user,
  #                                     mock_watch_users, mock_render):
  #   """Test the add users get handler displays users from a given group."""
  #   # pylint: disable=too-many-arguments
  #   mock_ds.return_value = None
  #   # Email address could refer to group or user
  #   group_key = 'foo@bar.mybusiness.com'
  #   mock_get_by_key.return_value = FAKE_USER_ARRAY
  #   self.testapp.get(PATHS['user_add_path'] + '?group_key=' + group_key)

  #   mock_get_users.assert_not_called()
  #   mock_get_user.assert_not_called()
  #   mock_ds.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
  #   mock_get_by_key.assert_called_once_with(group_key)
  #   mock_watch_users.assert_any_call('delete')
  #   mock_watch_users.assert_any_call('makeAdmin')
  #   mock_watch_users.assert_any_call('undelete')
  #   mock_watch_users.assert_any_call('update')
  #   mock_render.assert_called_once_with(FAKE_USER_ARRAY)

  # @patch('user._RenderAddUsersTemplate')
  # @patch('google_directory_service.GoogleDirectoryService.WatchUsers')
  # @patch('google_directory_service.GoogleDirectoryService.GetUserAsList')
  # @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  # @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  # @patch('google_directory_service.GoogleDirectoryService.__init__')
  # def testAddUsersGetHandlerWithUser(self, mock_ds, mock_get_users,
  #                                    mock_get_by_key, mock_get_user,
  #                                    mock_watch_users, mock_render):
  #   """Test the add users get handler displays a given user as requested."""
  #   # pylint: disable=too-many-arguments
  #   mock_ds.return_value = None
  #   # Email address could refer to group or user
  #   user_key = 'foo@bar.mybusiness.com'
  #   mock_get_user.return_value = FAKE_USER_ARRAY
  #   self.testapp.get(PATHS['user_add_path'] + '?user_key=' + user_key)

  #   mock_get_users.assert_not_called()
  #   mock_get_by_key.assert_not_called()
  #   mock_ds.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
  #   mock_get_user.assert_called_once_with(user_key)
  #   mock_watch_users.assert_any_call('delete')
  #   mock_watch_users.assert_any_call('makeAdmin')
  #   mock_watch_users.assert_any_call('undelete')
  #   mock_watch_users.assert_any_call('update')
  #   mock_render.assert_called_once_with(FAKE_USER_ARRAY)

  # @patch('user._RenderAddUsersTemplate')
  # @patch('google_directory_service.GoogleDirectoryService.WatchUsers')
  # @patch('google_directory_service.GoogleDirectoryService.GetUserAsList')
  # @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  # @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  # @patch('google_directory_service.GoogleDirectoryService.__init__')
  # def testAddUsersGetHandlerWithAll(self, mock_ds, mock_get_users,
  #                                   mock_get_by_key, mock_get_user,
  #                                   mock_watch_users, mock_render):
  #   """Test the add users get handler displays all users in a domain."""
  #   # pylint: disable=too-many-arguments
  #   mock_ds.return_value = None
  #   mock_get_users.return_value = FAKE_USER_ARRAY
  #   self.testapp.get(PATHS['user_add_path'] + '?get_all=true')

  #   mock_get_by_key.assert_not_called()
  #   mock_get_user.assert_not_called()
  #   mock_ds.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
  #   mock_get_users.assert_called_once_with()
  #   mock_watch_users.assert_any_call('delete')
  #   mock_watch_users.assert_any_call('makeAdmin')
  #   mock_watch_users.assert_any_call('undelete')
  #   mock_watch_users.assert_any_call('update')
  #   mock_render.assert_called_once_with(FAKE_USER_ARRAY)

  # @patch('user._RenderAddUsersTemplate')
  # @patch('google_directory_service.GoogleDirectoryService.WatchUsers')
  # @patch('google_directory_service.GoogleDirectoryService.GetUserAsList')
  # @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  # @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  # @patch('google_directory_service.GoogleDirectoryService.__init__')
  # def testAddUsersGetHandlerWithError(self, mock_ds, mock_get_users,
  #                                     mock_get_by_key, mock_get_user,
  #                                     mock_watch_users, mock_render):
  #   """Test the add users get handler fails gracefully."""
  #   # pylint: disable=too-many-arguments
  #   fake_status = '404'
  #   fake_response = MagicMock(status=fake_status)
  #   fake_content = b'some error content'
  #   fake_error = errors.HttpError(fake_response, fake_content)
  #   mock_ds.side_effect = fake_error
  #   mock_get_users.return_value = FAKE_USER_ARRAY
  #   self.testapp.get(PATHS['user_add_path'] + '?get_all=true')

  #   mock_ds.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
  #   mock_get_by_key.assert_not_called()
  #   mock_get_user.assert_not_called()
  #   mock_get_users.assert_not_called()
  #   mock_watch_users.assert_not_called()
  #   mock_render.assert_called_once_with([], fake_error)

  # @patch('user.User.InsertUsers')
  # def testAddUsersPostHandler(self, mock_insert):
  #   """Test the add users post handler calls to insert the specified users."""
  #   user_1 = {}
  #   user_1['primaryEmail'] = FAKE_EMAIL_1
  #   user_1['name'] = {}
  #   user_1['name']['fullName'] = FAKE_EMAIL_1
  #   user_2 = {}
  #   user_2['primaryEmail'] = FAKE_EMAIL_2
  #   user_2['name'] = {}
  #   user_2['name']['fullName'] = FAKE_EMAIL_2
  #   user_array = []
  #   user_array.append(user_1)
  #   user_array.append(user_2)
  #   data = '?selected_user={0}&selected_user={1}'.format(user_1, user_2)
  #   response = self.testapp.post(PATHS['user_add_path'] + data)

  #   mock_insert.assert_called_once_with(user_array)
  #   self.assertEqual(response.status_int, 302)
  #   self.assertTrue(PATHS['user_page_path'] in response.location)

  # @patch('user.User.InsertUsers')
  # def testAddUsersPostManualHandler(self, mock_insert):
  #   """Test add users manually calls to insert the specified user."""
  #   user_1 = {}
  #   user_1['primaryEmail'] = FAKE_EMAIL
  #   user_1['name'] = {}
  #   user_1['name']['fullName'] = FAKE_NAME
  #   user_array = []
  #   user_array.append(user_1)
  #   data = '?manual=true&user_name={0}&user_email={1}'.format(FAKE_NAME,
  #                                                             FAKE_EMAIL)
  #   response = self.testapp.post(PATHS['user_add_path'] + data)

  #   mock_insert.assert_called_once_with(user_array)
  #   self.assertEqual(response.status_int, 302)
  #   self.assertTrue(PATHS['user_page_path'] in response.location)


if __name__ == '__main__':
  unittest.main()
