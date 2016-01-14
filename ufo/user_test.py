"""Test user module functionality."""
import os

import flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import unittest

import database
import management_server
import models
import user

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

FAKE_EMAILS = ['foo@aol.com', 'bar@yahoo.com', 'baz@gmail.com']
FAKE_NAMES = ['joe', 'bob', 'mark']

class UserTest(unittest.TestCase):

  """Test user class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    self.db_uri = 'sqlite:///' + os.path.join(BASE_DIR, 'test.db')
    management_server.app.config['TESTING'] = True
    management_server.app.config['WTF_CSRF_ENABLED'] = False
    management_server.app.config['SQLALCHEMY_DATABASE_URI'] = self.db_uri
    self.app = management_server.app.test_client()
    # The code below is what was used for the prior initialization.
    # I'm keeping it around in case we switch back so I can find it again.
    # management_server.db.create_all()
    self.engine = create_engine(self.db_uri, convert_unicode=True)
    self.session = scoped_session(sessionmaker(autocommit=False,
                                               autoflush=False,
                                               bind=self.engine))
    database.Base.query = self.session.query_property()
    import models
    database.Base.metadata.create_all(bind=self.engine)

    self.mock_config = models.Config()
    self.mock_config.isConfigured = True
    self.mock_config.id = 0

    self.session.add(self.mock_config)
    self.session.commit()

  def tearDown(self):
    """Teardown the test db and instances."""
    # The code below is what was used for the prior tear down.
    # I'm keeping it around in case we switch back so I can find it again.
    # management_server.db.create_all()
    # management_server.db.session.remove()
    # management_server.db.drop_all()
    self.session.delete(self.mock_config)
    self.session.commit()
    self.session.close()

  def testListUsersHandler(self):
    """Test the list user handler displays users from the database."""
    fake_users = []
    for x in range(0, len(FAKE_EMAILS)):
      fake_user = models.User()
      fake_user.email = FAKE_EMAILS[x]
      fake_user.name = FAKE_NAMES[x]
      fake_users.append(fake_user)
      self.session.add(fake_user)
    self.session.commit()

    resp = self.app.get(flask.url_for('user_page_path'))
    user_list_output = resp.data

    self.assertEquals('Add Users' in user_list_output, True)
    click_user_string = 'Click a user below to view more details.'
    self.assertEquals(click_user_string in user_list_output, True)

    for x in range(0, len(FAKE_EMAILS)):
      self.assertEquals(FAKE_EMAILS[x] in user_list_output, True)
      details_link = ('/user/' + str(fake_users[x].id) + '/details')
      self.assertEquals(details_link in user_list_output, True)


if __name__ == '__main__':
  unittest.main()
