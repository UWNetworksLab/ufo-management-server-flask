"""Test for models module functionality."""

from mock import MagicMock
from mock import patch
import os

import flask
from flask.ext.testing import TestCase
import unittest

from . import app
from . import db
import models
import user

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

FAKE_PRIVATE_KEY = 'fakePrivateKey'

class UserTest(TestCase):
  """Test for models module functionality."""

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
    db.session.remove()
    db.drop_all()

  @patch('base64.urlsafe_b64encode')
  @patch.object(models.RSA._RSAobj, 'publickey')
  @patch('ufo.models.RSA._RSAobj.exportKey')
  @patch.object(models.RSA, 'generate')
  def testGenerateKeyPair(self, mock_rsa, mock_export_key, mock_public_key,
                          mock_encode):
    # Disabling the protected access check here intentionally so we can test a
    # private method.
    # pylint: disable=protected-access
    mock_encode.return_value = FAKE_PRIVATE_KEY
    mock_export_key.return_value = FAKE_PRIVATE_KEY
    mock_public_key.return_value.exportKey = mock_export_key
    mock_rsa.return_value.exportKey = mock_export_key
    mock_rsa.return_value.publickey = mock_public_key

    key_pair = models.User._GenerateKeyPair()

    mock_rsa.assert_called_once_with(2048)
    self.assertEqual(mock_export_key.call_count, 2)
    mock_public_key.assert_called_once_with()
    self.assertEqual(mock_encode.call_count, 2)
    mock_encode.assert_any_call(FAKE_PRIVATE_KEY)
    self.assertEqual(key_pair['public_key'], FAKE_PRIVATE_KEY)
    self.assertEqual(key_pair['private_key'], FAKE_PRIVATE_KEY)

if __name__ == '__main__':
  unittest.main()