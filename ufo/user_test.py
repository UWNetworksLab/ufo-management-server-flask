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


if __name__ == '__main__':
  unittest.main()
