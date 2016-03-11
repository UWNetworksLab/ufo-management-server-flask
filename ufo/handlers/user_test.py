"""Test user module functionality."""
import base64
import json
import unittest

import flask
from googleapiclient import errors
from mock import MagicMock
from mock import patch
from werkzeug.datastructures import MultiDict
from werkzeug.datastructures import ImmutableMultiDict

from ufo import base_test
from ufo.database import models
from ufo.handlers import user
# I practically have to shorten this name so every single line doesn't go
# over. If someone can't understand, they can use ctrl+f to look it up here.
from ufo.services import google_directory_service as gds
from ufo.services import oauth


FAKE_DIRECTORY_USER_ARRAY = []
FAKE_USERS_FOR_DISPLAY_ARRAY = []
for fake_email_and_name in base_test.FAKE_EMAILS_AND_NAMES:
  fake_directory_user = {}
  fake_directory_user['primaryEmail'] = fake_email_and_name['email']
  fake_directory_user['name'] = {}
  fake_directory_user['name']['fullName'] = fake_email_and_name['name']
  fake_directory_user['email'] = fake_email_and_name['email']
  fake_directory_user['role'] = 'MEMBER'
  fake_directory_user['type'] = 'USER'
  fake_user_for_display = {
      'name': fake_email_and_name['name'],
      'email': fake_email_and_name['email']
  }
  FAKE_DIRECTORY_USER_ARRAY.append(fake_directory_user)
  FAKE_USERS_FOR_DISPLAY_ARRAY.append(fake_user_for_display)

FAKE_CREDENTIAL = 'Look at me. I am a credential!'

FAKE_MODEL_USER = MagicMock(email=base_test.FAKE_EMAILS_AND_NAMES[0]['email'],
                            name=base_test.FAKE_EMAILS_AND_NAMES[0]['name'],
                            private_key='private key foo',
                            public_key='public key bar',
                            is_key_revoked=False)


class UserTest(base_test.BaseTest):
  """Test user class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(UserTest, self).setUp()
    super(UserTest, self).setup_config()

  def testListUsersHandler(self):
    """Test the list user handler gets users from the database."""
    users = []
    for fake_email_and_name in base_test.FAKE_EMAILS_AND_NAMES:
      user = models.User(email=fake_email_and_name['email'],
                         name=fake_email_and_name['name'],
                         private_key=fake_email_and_name['pri'],
                         public_key=fake_email_and_name['pub'])
      user.save()
      users.append(user)

    resp = self.client.get(flask.url_for('user_list'))
    user_list_output = json.loads(resp.data)['items']

    self.assertEquals(len(user_list_output),
                      len(base_test.FAKE_EMAILS_AND_NAMES))

    for user in users:
      self.assertIn(user.to_dict(), user_list_output)

  @patch.object(user, '_get_users_to_add')
  def testAddUsersGetHandler(self, mock_render):
    """Test the add users get handler returns _get_users_to_add's result."""
    return_text = '<html>something here </html>'
    mock_render.return_value = return_text
    resp = self.client.get(flask.url_for('add_user'))

    self.assertEquals(resp.data, return_text)

  @patch('flask.Response')
  @patch.object(oauth, 'getSavedCredentials')
  def testAddUsersGetNoCredentials(self, mock_get_saved_credentials,
                                  mock_response):
    """Test add user get should display an error when oauth isn't set."""
    mock_get_saved_credentials.return_value = None
    mock_response.return_value = ''

    response = self.client.get(flask.url_for('add_user'))

    args, kwargs = mock_response.call_args
    json_output = json.loads(args[0])
    self.assertEquals([], json_output['directory_users'])
    self.assertIsNotNone(json_output['error'])
    self.assertEquals('application/json', kwargs['mimetype'])

  @patch('flask.Response')
  @patch.object(oauth, 'getSavedCredentials')
  @patch.object(gds.GoogleDirectoryService, '__init__')
  def testAddUsersGetNoParam(self, mock_gds, mock_get_saved_credentials,
                            mock_response):
    """Test add user get should display no users on initial get."""
    mock_get_saved_credentials.return_value = FAKE_CREDENTIAL
    mock_gds.return_value = None
    mock_response.return_value = ''

    response = self.client.get(flask.url_for('add_user'))

    args, kwargs = mock_response.call_args
    json_output = json.loads(args[0])
    self.assertEquals([], json_output['directory_users'])
    self.assertEquals('application/json', kwargs['mimetype'])

  @patch('flask.Response')
  @patch.object(oauth, 'getSavedCredentials')
  @patch.object(gds.GoogleDirectoryService, 'GetUsersByGroupKey')
  @patch.object(gds.GoogleDirectoryService, '__init__')
  def testAddUsersGetWithGroup(self, mock_gds, mock_get_by_key,
                              mock_get_saved_credentials,
                              mock_response):
    """Test add user get should display users from a given group."""
    mock_get_saved_credentials.return_value = FAKE_CREDENTIAL
    mock_gds.return_value = None
    # Email address could refer to group or user
    group_key = 'foo@bar.mybusiness.com'
    mock_get_by_key.return_value = FAKE_DIRECTORY_USER_ARRAY
    mock_response.return_value = ''

    response = self.client.get(flask.url_for('add_user', group_key=group_key))

    args, kwargs = mock_response.call_args
    json_output = json.loads(args[0])
    self.assertEquals(FAKE_USERS_FOR_DISPLAY_ARRAY,
                      json_output['directory_users'])
    self.assertEquals('application/json', kwargs['mimetype'])

  @patch('flask.Response')
  @patch.object(oauth, 'getSavedCredentials')
  @patch.object(gds.GoogleDirectoryService, 'GetUserAsList')
  @patch.object(gds.GoogleDirectoryService, '__init__')
  def testAddUsersGetWithUser(self, mock_gds, mock_get_user,
                             mock_get_saved_credentials,
                             mock_response):
    """Test add user get should display a given user as requested."""
    mock_get_saved_credentials.return_value = FAKE_CREDENTIAL
    mock_gds.return_value = None
    # Email address could refer to group or user
    user_key = 'foo@bar.mybusiness.com'
    mock_get_user.return_value = FAKE_DIRECTORY_USER_ARRAY
    mock_response.return_value = ''

    response = self.client.get(flask.url_for('add_user', user_key=user_key))

    args, kwargs = mock_response.call_args
    json_output = json.loads(args[0])
    self.assertEquals(FAKE_USERS_FOR_DISPLAY_ARRAY,
                      json_output['directory_users'])
    self.assertEquals('application/json', kwargs['mimetype'])

  @patch('flask.Response')
  @patch.object(oauth, 'getSavedCredentials')
  @patch.object(gds.GoogleDirectoryService, 'GetUsers')
  @patch.object(gds.GoogleDirectoryService, '__init__')
  def testAddUsersGetWithAll(self, mock_gds, mock_get_users,
                            mock_get_saved_credentials,
                            mock_response):
    """Test add user get should display all users in a domain."""
    mock_get_saved_credentials.return_value = FAKE_CREDENTIAL
    mock_gds.return_value = None
    mock_get_users.return_value = FAKE_DIRECTORY_USER_ARRAY
    mock_response.return_value = ''

    response = self.client.get(flask.url_for('add_user', get_all=True))

    args, kwargs = mock_response.call_args
    json_output = json.loads(args[0])
    self.assertEquals(FAKE_USERS_FOR_DISPLAY_ARRAY,
                      json_output['directory_users'])
    self.assertEquals('application/json', kwargs['mimetype'])

  @patch('flask.Response')
  @patch.object(oauth, 'getSavedCredentials')
  @patch.object(gds.GoogleDirectoryService, '__init__')
  def testAddUsersGetWithError(self, mock_gds, mock_get_saved_credentials,
                              mock_response):
    """Test add users get fails gracefully when a resource isn't found.

    We need to catch errors from the google directory service module since we
    have not yet implemented robust error handling. Here I'm simulating an
    exception in the directory service and asserting that we catch it and still
    render the add_user page along with the error rather than barfing
    completely.
    """
    mock_get_saved_credentials.return_value = FAKE_CREDENTIAL
    fake_status = '404'
    fake_response = MagicMock(status=fake_status)
    fake_content = b'some error content'
    fake_error = errors.HttpError(fake_response, fake_content)
    mock_gds.side_effect = fake_error
    mock_response.return_value = ''

    response = self.client.get(flask.url_for('add_user'))

    args, kwargs = mock_response.call_args
    json_output = json.loads(args[0])
    self.assertEquals([], json_output['directory_users'])
    self.assertEquals(str(fake_error), json_output['error'])
    self.assertEquals('application/json', kwargs['mimetype'])

  def testAddUsersPostHandler(self):
    """Test the add users post handler calls to insert the specified users."""
    response = self.create_users_with_google_directory_service_post()

    users_count = models.User.query.count()
    self.assertEquals(len(base_test.FAKE_EMAILS_AND_NAMES), users_count)

    users_in_db = models.User.query.all()
    self.assertEquals(len(base_test.FAKE_EMAILS_AND_NAMES), len(users_in_db))

    for fake_email_and_name in base_test.FAKE_EMAILS_AND_NAMES:
      query = models.User.query.filter_by(email=fake_email_and_name['email'])
      user_in_db = query.one_or_none()
      self.assertEqual(fake_email_and_name['name'], user_in_db.name)
      self.assertEqual(user_in_db.domain, self.config.domain)

    self.assertEqual(response.data, self.client.get(flask.url_for('user_list')).data)

  def testAddUsersPostManualHandler(self):
    """Test add users manually calls to insert the specified user."""
    response = self.create_user_with_manual_post()

    query = models.User.query.filter_by(
        email=base_test.FAKE_EMAILS_AND_NAMES[0]['email'])
    user_in_db = query.one_or_none()
    self.assertIsNotNone(user_in_db)
    self.assertEqual(base_test.FAKE_EMAILS_AND_NAMES[0]['name'],
                     user_in_db.name)
    self.assertEqual(base_test.FAKE_EMAILS_AND_NAMES[0]['email'],
                     user_in_db.email)
    self.assertIsNone(user_in_db.domain)

    self.assertEqual(response.data, self.client.get(flask.url_for('user_list')).data)

  @patch('flask.render_template')
  def testUserDetailsGet(self, mock_render_template):
    """Test the user details handler calls to render a user's information."""
    created_user = self._CreateAndSaveFakeUser()
    mock_render_template.return_value = ''

    response = self.client.get(flask.url_for('user_details', user_id=created_user.id))

    args, kwargs = mock_render_template.call_args
    self.assertEquals('user_details.html', args[0])
    self.assertEquals(created_user, kwargs['user'])
    self.assertNotIn('invite_url', kwargs)

  @patch('flask.render_template')
  def testUserDetailsGetWithInvite(self, mock_render_template):
    """Test the user details handler renders a valid invite code."""
    fake_ip = '0.1.2.3'
    proxy_server = models.ProxyServer(ip_address=fake_ip)
    proxy_server.save()
    created_user = self._CreateAndSaveFakeUser()
    mock_render_template.return_value = ''

    response = self.client.get(flask.url_for('user_details',
                                             user_id=created_user.id))

    args, kwargs = mock_render_template.call_args
    self.assertEquals('user_details.html', args[0])
    self.assertEquals(created_user, kwargs['user'])
    invite_url = kwargs['invite_url']
    self.assertIn(user.INVITE_CODE_URL_PREFIX, invite_url)
    invite_code_base64 = invite_url[len(user.INVITE_CODE_URL_PREFIX):]

    invite_code_json = base64.urlsafe_b64decode(invite_code_base64)
    invite_code = json.loads(invite_code_json)

    self.assertEquals('Cloud', invite_code['networkName'])
    self.assertEquals(fake_ip, invite_code['networkData']['host'])
    self.assertEquals(created_user.email,
                      invite_code['networkData']['user'])
    self.assertEquals(created_user.private_key,
                      invite_code['networkData']['pass'])

  def testDeleteUserPostHandler(self):
    """Test the delete user handler calls to delete the specified user."""
    user = self._CreateAndSaveFakeUser()

    post_data = {'user_id': json.dumps(user.id)}
    response = self.client.post(flask.url_for('delete_user'), data=post_data)

    user = models.User.query.get(user.id)
    self.assertIsNone(user)
    self.assertEqual(response.data, self.client.get(flask.url_for('user_list')).data)

  def testUserGetNewKeyPairHandler(self):
    """Test get new key pair handler regenerates a key pair for the user."""
    user = self._CreateAndSaveFakeUser()
    user_private_key = user.private_key

    post_data = {'user_id': json.dumps(user.id)}
    response = self.client.post(flask.url_for('user_get_new_key_pair'),
                                data=post_data, follow_redirects=False)

    self.assertNotEqual(user_private_key, user.private_key)

    self.assert_redirects(response, flask.url_for('user_list'))

  def testUserGetInviteCode(self):
    """Test the user get invite code returns a valid invite code."""
    fake_ip = '0.1.2.3'
    proxy_server = models.ProxyServer(ip_address=fake_ip)
    proxy_server.save()
    created_user = self._CreateAndSaveFakeUser()

    get_data = {'user_id': created_user.id}
    resp = self.client.get(flask.url_for('user_get_invite_code'),
                           query_string=get_data)
    invite_url = str(json.loads(resp.data)['invite_code'])

    self.assertIn(user.INVITE_CODE_URL_PREFIX, invite_url)
    invite_code_base64 = invite_url[len(user.INVITE_CODE_URL_PREFIX):]
    invite_code_json = base64.urlsafe_b64decode(invite_code_base64)
    invite_code = json.loads(invite_code_json)

    self.assertEquals('Cloud', invite_code['networkName'])
    self.assertEquals(fake_ip, invite_code['networkData']['host'])
    self.assertEquals(created_user.email, invite_code['networkData']['user'])
    self.assertEquals(created_user.private_key,
                      invite_code['networkData']['pass'])

  def testUserToggleRevokedHandler(self):
    """Test toggle revoked handler changes the revoked status for a user."""
    user = self._CreateAndSaveFakeUser()
    initial_revoked_status = user.is_key_revoked
    user.did_cron_revoke = True
    user.save()

    post_data = {'user_id': json.dumps(user.id)}
    response = self.client.post(flask.url_for('user_toggle_revoked'),
                                data=post_data, follow_redirects=False)

    self.assertEquals(not initial_revoked_status, user.is_key_revoked)
    self.assertEquals(False, user.did_cron_revoke)
    self.assert_redirects(response, flask.url_for('user_list'))

  def _CreateAndSaveFakeUser(self):
    """Create a fake user object, and save it into db."""
    user = models.User(email=base_test.FAKE_EMAILS_AND_NAMES[0]['email'],
                       name=base_test.FAKE_EMAILS_AND_NAMES[0]['name'])
    return user.save()


if __name__ == '__main__':
  unittest.main()
