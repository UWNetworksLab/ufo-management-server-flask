"""Test admin module functionality."""
import json
import unittest

import flask
from mock import MagicMock
from mock import patch

import ufo
from ufo import base_test
from ufo.database import models
from ufo.handlers import admin


MOCK_ADMIN_EMAIL = 'foobar@admin.com'
MOCK_ADMIN_PASSWORD = 'random password'
MOCK_ADMIN_DATA = {
  'admin_email': json.dumps(MOCK_ADMIN_EMAIL),
  'admin_password': json.dumps(MOCK_ADMIN_PASSWORD)
}
NEW_MOCK_ADMIN_PASSWORD = 'new different fake random password'


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
    admin_list_output = json.loads(resp.data[len(ufo.XSSI_PREFIX):])['items']

    self.assertEquals(len(admin_list_output), 1)
    test_admin = admin_list_output[0]
    self.assertEquals(base_test.FAKE_ADMIN_EMAIL, test_admin['email'])
    self.assertNotIn('password', test_admin)

  def testAddAdminHandler(self):
    """Test the add admin handler calls to insert the specified admin."""
    admin_user = models.AdminUser.get_by_email(MOCK_ADMIN_EMAIL)
    self.assertIsNone(admin_user)

    response =  self.client.post(flask.url_for('add_admin'),
                                 data=MOCK_ADMIN_DATA,
                                 follow_redirects=False)

    admin_user = models.AdminUser.get_by_email(MOCK_ADMIN_EMAIL)
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
    query = models.AdminUser.query.filter_by(email=MOCK_ADMIN_EMAIL)
    self.assertEqual(1, query.count())
    admin_in_db = query.one_or_none()
    self.assertIsNotNone(admin_in_db)
    self.assertEqual(MOCK_ADMIN_EMAIL, admin_in_db.email)
    self.assertIsNotNone(admin_in_db.password)

  def testDeleteAdminPostHandler(self):
    """Test the delete admin handler calls to delete the specified admin."""
    self.client.post(flask.url_for('add_admin'), data=MOCK_ADMIN_DATA,
                     follow_redirects=False)
    query = models.AdminUser.query.filter_by(email=MOCK_ADMIN_EMAIL)
    admin_in_db = query.one_or_none()
    admin_id = admin_in_db.id

    post_data = {'admin_id': json.dumps(admin_id)}
    response = self.client.post(flask.url_for('delete_admin'), data=post_data)

    admin_user = models.AdminUser.query.get(admin_id)
    self.assertIsNone(admin_user)
    self.assert_redirects(response, flask.url_for('admin_list'))

  def testLastAdminCannotBeDeleted(self):
    """Test deleting the last admin throws an exception."""
    all_admins = models.AdminUser.query.all()
    self.assertEqual(1, len(all_admins))
    admin_id = all_admins[0].id

    post_data = {'admin_id': json.dumps(admin_id)}
    response = self.client.post(flask.url_for('delete_admin'), data=post_data)

    all_admins = models.AdminUser.query.all()
    self.assertEqual(1, len(all_admins))
    admin_in_db = all_admins[0]
    self.assertIsNotNone(admin_in_db)

  def testChangeAdminPasswordHandler(self):
    """Test the change admin password handler modified the admin's password."""
    # Use the admin setup by the base test since that is who is logged in.
    query = models.AdminUser.query.filter_by(email=base_test.FAKE_ADMIN_EMAIL)
    admin_in_db = query.one_or_none()
    admin_id = admin_in_db.id
    self.assertTrue(admin_in_db.does_password_match(
        base_test.FAKE_ADMIN_PASSWORD))
    self.assertFalse(admin_in_db.does_password_match(NEW_MOCK_ADMIN_PASSWORD))

    post_data = {
      'old_password': json.dumps(base_test.FAKE_ADMIN_PASSWORD),
      'new_password': json.dumps(NEW_MOCK_ADMIN_PASSWORD)
    }
    response = self.client.post(flask.url_for('change_admin_password'),
                                data=post_data)

    admin_user = models.AdminUser.query.get(admin_id)
    self.assertTrue(admin_in_db.does_password_match(NEW_MOCK_ADMIN_PASSWORD))
    self.assertFalse(admin_in_db.does_password_match(
        base_test.FAKE_ADMIN_PASSWORD))
    self.assert_redirects(response, flask.url_for('admin_list'))

  def testChangeAdminPasswordFailsWithIncorrectPassword(self):
    """Test change admin password rejects if the current password is wrong."""
    # Use the admin setup by the base test since that is who is logged in.
    query = models.AdminUser.query.filter_by(email=base_test.FAKE_ADMIN_EMAIL)
    admin_in_db = query.one_or_none()
    admin_id = admin_in_db.id
    self.assertTrue(admin_in_db.does_password_match(
        base_test.FAKE_ADMIN_PASSWORD))
    self.assertFalse(admin_in_db.does_password_match(NEW_MOCK_ADMIN_PASSWORD))

    post_data = {
      'admin_id': json.dumps(admin_id),
      # new password is not the old one
      'old_password': json.dumps(NEW_MOCK_ADMIN_PASSWORD),
      'new_password': json.dumps(NEW_MOCK_ADMIN_PASSWORD)
    }
    response = self.client.post(flask.url_for('change_admin_password'),
                                data=post_data)

    admin_user = models.AdminUser.query.get(admin_id)
    self.assertTrue(admin_in_db.does_password_match(
        base_test.FAKE_ADMIN_PASSWORD))
    self.assertFalse(admin_in_db.does_password_match(NEW_MOCK_ADMIN_PASSWORD))


if __name__ == '__main__':
  unittest.main()
