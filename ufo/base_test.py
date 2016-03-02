"""Base test with common setup and teardown."""

import json

import flask
from flask.ext.testing import TestCase

import ufo
from ufo.database import models

FAKE_DOMAIN = 'my.fake.domain.com.edu.gov.net'
FAKE_EMAILS_AND_NAMES = [
  {'email': 'foo@aol.com', 'name': 'joe', 'pri': 'foopri', 'pub': 'foopub'},
  {'email': 'bar@yahoo.com', 'name': 'bob', 'pri': 'barpri', 'pub': 'barpub'},
  {'email': 'baz@gmail.com', 'name': 'mark', 'pri': 'bazpri', 'pub': 'bazpub'}
]


class BaseTest(TestCase):
  """Base test with comment setup and teardown."""

  def create_app(self):
    ufo.app.config.from_object('config.TestConfiguration')
    return ufo.app

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    ufo.db.create_all()

  def setup_config(self):
    """Setup the config that is needed for @setup_required decorator."""
    self.config = models.Config()
    self.config.isConfigured = True
    self.config.domain = FAKE_DOMAIN
    self.config.id = 0

    self.config.save()

  def tearDown(self):
    ufo.db.session.remove()
    ufo.db.drop_all()

  def CreateUserWithManualPost(self):
    """Post a manually added user and return the response.

    Returns:
      The response object from the post.
    """
    mock_user = {
      'email': FAKE_EMAILS_AND_NAMES[0]['email'],
      'name': FAKE_EMAILS_AND_NAMES[0]['name']
    }
    data = {'users': json.dumps([mock_user]), 'manual': 'true'}
    return self.client.post(flask.url_for('add_user'), data=data)

  def CreateUsersWithGoogleDirectoryServicePost(self):
    """Post several users added from GDS and return the response.

    Returns:
      The response object from the post.
    """
    mock_users = []
    for fake_email_and_name in FAKE_EMAILS_AND_NAMES:
      mock_user = {
        'email': fake_email_and_name['email'],
        'name': fake_email_and_name['name']
      }
      mock_users.append(mock_user)

    data = {'users': json.dumps(mock_users)}
    return self.client.post(flask.url_for('add_user'), data=data)
