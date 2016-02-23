"""Test for models module functionality."""

from mock import MagicMock
from mock import patch
import os
import unittest

import base_test
import models
import user

from Crypto.PublicKey import RSA


FAKE_PRIVATE_KEY = 'fakePrivateKey'


class UserTest(base_test.BaseTest):
  """Test for models module functionality."""

  def testGenerateKeyPair(self):
    """Whether the generated key_pair is valid, and with correct size."""
    user = models.User()
    rsa_public_key = RSA.importKey(user.public_key)
    rsa_private_key = RSA.importKey(user.private_key)

    self.assertEqual(2048, rsa_public_key.size() + 1)
    self.assertEqual(2048, rsa_private_key.size() + 1)

    message = os.urandom(8)
    encrypted_message = rsa_public_key.encrypt(message, 12345)
    self.assertEqual(message, rsa_private_key.decrypt(encrypted_message))

  def testRegenerateKeyPair(self):
    user = models.User()
    original_public_key = user.public_key
    original_private_key = user.private_key

    user.regenerate_key_pair()
    self.assertNotEqual(original_public_key, user.public_key)
    self.assertNotEqual(original_private_key, user.private_key)

  def testToDict(self):
    user = models.User()
    user.is_key_revoked = False
    user_dict = user.to_dict()

    self.assertEqual(user_dict['email'], user.email)
    self.assertEqual(user_dict['name'], user.name)
    self.assertEqual(user_dict['private_key'], user.private_key)
    self.assertEqual(user_dict['public_key'], user.public_key)
    self.assertEqual(user_dict['access'], models.NOT_REVOKED_TEXT)

    user.is_key_revoked = True
    user_dict = user.to_dict()
    self.assertEqual(user_dict['access'], models.REVOKED_TEXT)


if __name__ == '__main__':
  unittest.main()
