"""Test key distributor module functionality."""

from Crypto.PublicKey import RSA
from mock import patch

from ufo import base_test
from ufo.database import models
from ufo.services import key_distributor


class KeyDistributorTest(base_test.BaseTest):
  """Test key distributor class functionality."""

  def testUnrevokedUsersAreInKeyString(self):
    """Test unrevoked users are in key string.."""
    fake_users = []
    for fake_email_and_name in base_test.FAKE_EMAILS_AND_NAMES:
      fake_user = models.User(email=fake_email_and_name['email'],
                              name=fake_email_and_name['name'],
                              is_key_revoked=False)
      fake_user.save()
      fake_users.append(fake_user)

    key_string = key_distributor.KeyDistributor().make_key_string()

    # There should be no PEM-format keys in an authorized_keys file
    self.assertEquals(0, key_string.count('END PUBLIC KEY'))

    for fake_user in fake_users:
      self.assertIn(fake_user.email, key_string)
      self.assertIn(
          RSA.importKey(fake_user.public_key).exportKey('OpenSSH'),
          key_string)

  def testRevokedUsersAreNotInKeyString(self):
    """Test revoked users are not in key string.."""
    fake_users = []
    for fake_email_and_name in base_test.FAKE_EMAILS_AND_NAMES:
      fake_user = models.User(email=fake_email_and_name['email'],
                              name=fake_email_and_name['name'],
                              is_key_revoked=True)
      fake_user.save()
      fake_users.append(fake_user)

    key_string = key_distributor.KeyDistributor().make_key_string()

    self.assertFalse(key_string)


if __name__ == '__main__':
  unittest.main()
