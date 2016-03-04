"""Test regex module functionality."""

import re
import unittest

from Crypto.PublicKey import RSA

from ufo.services import regex


POTENTIAL_EMAIL_ADDRESSES = [
  'foo@bar.baz',
  'foo@bar.com',
  'loooooooooooongaddress@comcast.net'
]

class RegexTest(unittest.TestCase):
  """Test regex module functionality."""

  def testDictionaryHasPatternsAndErrors(self):
    """Test the list user handler gets users from the database."""
    self.assertIn('emailValidationPattern',
                  regex.REGEXES_AND_ERRORS_DICTIONARY)
    self.assertIn('emailValidationError', regex.REGEXES_AND_ERRORS_DICTIONARY)
    self.assertIn('keyLookupPattern', regex.REGEXES_AND_ERRORS_DICTIONARY)
    self.assertIn('keyLookupError', regex.REGEXES_AND_ERRORS_DICTIONARY)
    self.assertIn('publicKeyPattern', regex.REGEXES_AND_ERRORS_DICTIONARY)
    self.assertIn('publicKeyError', regex.REGEXES_AND_ERRORS_DICTIONARY)
    self.assertIn('privateKeyPattern', regex.REGEXES_AND_ERRORS_DICTIONARY)
    self.assertIn('privateKeyError', regex.REGEXES_AND_ERRORS_DICTIONARY)
    self.assertIn('ipAddressPattern', regex.REGEXES_AND_ERRORS_DICTIONARY)
    self.assertIn('ipAddressError', regex.REGEXES_AND_ERRORS_DICTIONARY)

  def testEmailPatternMatchesValidEmailAddresses(self):
    """Test the email regex pattern matches valid email addresses."""
    pattern = regex.REGEXES_AND_ERRORS_DICTIONARY['emailValidationPattern']
    self._patternMatchHelper(pattern, POTENTIAL_EMAIL_ADDRESSES)

  def testKeyPatternMatchesValidEmailAddressOrUniqueId(self):
    """Test the key lookup regex pattern matches valid email address or id."""
    pattern = regex.REGEXES_AND_ERRORS_DICTIONARY['keyLookupPattern']
    potentialIds = [
      'randomMadeUpIdThatCouldBeAnyAlphaNumeric',
      '0123456789',
      'randomMadeUpIdThatCouldBeAnyAlphaNumeric0123456789'
    ]
    potentialEmailsAndIds = POTENTIAL_EMAIL_ADDRESSES + potentialIds
    self._patternMatchHelper(pattern, potentialEmailsAndIds)

  def testPublicKeyPatternMatchesValidPublicKeys(self):
    """Test the public key regex pattern matches valid public keys."""
    pattern = regex.REGEXES_AND_ERRORS_DICTIONARY['publicKeyPattern']
    potentialPublicKeys = []
    for email in POTENTIAL_EMAIL_ADDRESSES:
      ssh_key = RSA.generate(2048).publickey().exportKey('OpenSSH')
      potentialPublicKeys.append(ssh_key + ' ' + email)
    self._patternMatchHelper(pattern, potentialPublicKeys)

  def testPrivateKeyPatternMatchesValidPrivateKeys(self):
    """Test the private key regex pattern matches valid private keys."""
    pattern = regex.REGEXES_AND_ERRORS_DICTIONARY['privateKeyPattern']
    potentialPrivateKeys = []
    for email in POTENTIAL_EMAIL_ADDRESSES:
      private_key = RSA.generate(2048).exportKey()
      potentialPrivateKeys.append(private_key)
    self._patternMatchHelper(pattern, potentialPrivateKeys)

  def testIPAddressPatternMatchesValidIPAddresses(self):
    """Test the ip address regex pattern matches valid ip v4/v6 addresses."""
    pattern = regex.REGEXES_AND_ERRORS_DICTIONARY['ipAddressPattern']
    # IP v6 addresses taken from example of wikipedia at this address:
    # https://en.wikipedia.org/wiki/IPv6_address
    # Feel free to add more as necessary.
    potentialIps = [
      '127.0.0.0',
      '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
      '2001:db8:85a3:0:0:8a2e:370:7334',
      '0:0:0:0:0:0:0:1',
      '0:0:0:0:0:0:0:0',
      '::1',
      '::',
    ]
    self._patternMatchHelper(pattern, potentialIps)

  def _patternMatchHelper(self, pattern, potentialMatchList):
    """Test the pattern matches everything on the list given.

    Args:
      pattern: The regular expression to run against potential matches.
      potentialMatchList: A list of strings which should all match the pattern.
    """
    for potentialMatch in potentialMatchList:
      match = re.search(pattern, potentialMatch)
      self.assertEquals(match.group(0), potentialMatch)


if __name__ == '__main__':
  unittest.main()
