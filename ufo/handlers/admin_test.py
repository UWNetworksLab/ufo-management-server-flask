"""Test admin module functionality."""
import json
import unittest

import flask
from mock import MagicMock
from mock import patch

from ufo import base_test
from ufo.database import models
from ufo.handlers import admin


MOCK_ADMIN_USERNAME = 'foobar admin'
MOCK_ADMIN_PASSWORD = 'random password'
MOCK_ADMIN_DATA = {
  'admin_username': json.dumps(MOCK_ADMIN_USERNAME),
  'admin_password': json.dumps(MOCK_ADMIN_PASSWORD)
}


class AdminTest(base_test.BaseTest):
  """Test admin class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(AdminTest, self).setUp()
    super(AdminTest, self).setup_config()
    super(AdminTest, self).setup_auth()

  def testListAdminsHandler(self):
    """Test the list admin handler gets admins from the database."""
    resp = self.client.get(flask.url_for('admin_list'))
    admin_list_output = json.loads(resp.data)['items']

    self.assertEquals(len(admin_list_output), 1)
    test_admin = admin_list_output[0]
    self.assertEquals(base_test.FAKE_ADMIN_USERNAME, test_admin['username'])
    self.assertNotIn('password', test_admin)

  def testAddAdminHandler(self):
    """Test the add admin handler calls to insert the specified admin."""
    admin_user = models.AdminUser.get_by_username(MOCK_ADMIN_USERNAME)
    self.assertIsNone(admin_user)

    response =  self.client.post(flask.url_for('add_admin'),
                                 data=MOCK_ADMIN_DATA,
                                 follow_redirects=False)

    admin_user = models.AdminUser.get_by_username(MOCK_ADMIN_USERNAME)
    self.assertIsNotNone(admin_user)

    self.assert_redirects(response, flask.url_for('admin_list'))

  def testAdminCanNotBeAddedMoreThanOnce(self):
    """Test that admin can not added more than once."""
    response =  self.client.post(flask.url_for('add_admin'),
                                 data=MOCK_ADMIN_DATA,
                                 follow_redirects=False)
    response =  self.client.post(flask.url_for('add_admin'),
                                 data=MOCK_ADMIN_DATA,
                                 follow_redirects=False)
    query = models.AdminUser.query.filter_by(username=MOCK_ADMIN_USERNAME)
    self.assertEqual(1, query.count())
    admin_in_db = query.one_or_none()
    self.assertIsNotNone(admin_in_db)
    self.assertEqual(MOCK_ADMIN_USERNAME, admin_in_db.username)
    self.assertIsNotNone(admin_in_db.password)

  def testDeleteAdminPostHandler(self):
    """Test the delete admin handler calls to delete the specified admin."""
    response =  self.client.post(flask.url_for('add_admin'),
                                 data=MOCK_ADMIN_DATA,
                                 follow_redirects=False)
    query = models.AdminUser.query.filter_by(username=MOCK_ADMIN_USERNAME)
    admin_in_db = query.one_or_none()
    admin_id = admin_in_db.id

    post_data = {'admin_id': json.dumps(admin_id)}
    response = self.client.post(flask.url_for('delete_admin'), data=post_data)

    admin_user = models.AdminUser.query.get(admin_id)
    self.assertIsNone(admin_user)
    self.assert_redirects(response, flask.url_for('admin_list'))


if __name__ == '__main__':
  unittest.main()
