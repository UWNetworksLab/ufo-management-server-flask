"""Test for models module functionality."""

from mock import MagicMock
from mock import patch
import os
import unittest

import base_test
import models
import user


FAKE_PRIVATE_KEY = 'fakePrivateKey'


class UserTest(base_test.BaseTest):
  """Test for models module functionality."""

  @patch.object(models.RSA._RSAobj, 'publickey')
  @patch('ufo.models.RSA._RSAobj.exportKey')
  @patch.object(models.RSA, 'generate')
  def testGenerateKeyPair(self, mock_rsa, mock_export_key, mock_public_key):
    # Disabling the protected access check here intentionally so we can test a
    # private method.
    # pylint: disable=protected-access
    mock_export_key.return_value = FAKE_PRIVATE_KEY
    mock_public_key.return_value.exportKey = mock_export_key
    mock_rsa.return_value.exportKey = mock_export_key
    mock_rsa.return_value.publickey = mock_public_key

    key_pair = models.User._GenerateKeyPair()

    mock_rsa.assert_called_once_with(2048)
    self.assertEqual(mock_export_key.call_count, 2)
    mock_public_key.assert_called_once_with()
    self.assertEqual(key_pair['public_key'], FAKE_PRIVATE_KEY)
    self.assertEqual(key_pair['private_key'], FAKE_PRIVATE_KEY)

if __name__ == '__main__':
  unittest.main()
