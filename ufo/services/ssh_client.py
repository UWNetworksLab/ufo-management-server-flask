import base64
import StringIO
import socket

import paramiko
from paramiko import rsakey
from paramiko import dsskey
from paramiko import ecdsakey


class InvalidKeyTypeException(Exception):
  pass


class SSHConnectionException(Exception):
  code = 500
  message = 'Unable to establish ssh connection.'


RSA_KEY_TYPE = 'ssh-rsa'
DSS_KEY_TYPE = 'ssh-dss'
EC_KEY_TYPE = 'ecdsa-sha2-nistp256'


class SSHClient(paramiko.SSHClient):
  """An SSH client that uses a ProxyServer model to set up a connection
  """

  key_type_to_tag_map = {
      RSA_KEY_TYPE: 'RSA',
      DSS_KEY_TYPE: 'DSA',
      EC_KEY_TYPE: 'EC',
      }

  def connect(self, proxy_server):
    """Establish a connection with the target proxy server.

    Args:
      proxy_server: db representation of a proxy server.

    Returns:
      A ssh client with an established connection.

    Raises:
      InvalidKeyTypeException: An exception that occurs if the public
          or private key is invalid.
      SSHConnectionException: An exception that occurs if ssh connection
          can not be established.
    """
    if not self.validate_key_type(proxy_server.host_public_key_type):
      raise InvalidKeyTypeException('Invalid public key type')
    if not self.validate_key_type(proxy_server.ssh_private_key_type):
      raise InvalidKeyTypeException('Invalid private key type')

    # add proper verification for the server
    host_keys = self.get_host_keys()
    host_keys.clear()

    public_key = self.public_key_data_to_object(
        proxy_server.host_public_key_type,
        proxy_server.host_public_key)

    host_keys.add(
        proxy_server.ip_address,
        proxy_server.host_public_key_type,
        public_key)

    # setup the auntentication information needed to connect to the server
    authentication_key = self.private_key_data_to_object(
        proxy_server.ssh_private_key_type,
        proxy_server.ssh_private_key)

    try:
      return super(SSHClient, self).connect(
          proxy_server.ip_address,
          username='root',
          pkey=authentication_key,
          allow_agent=False,
          look_for_keys=False)
    except (paramiko.AuthenticationException, paramiko.BadHostKeyException,
            paramiko.SSHException, socket.error):
      raise SSHConnectionException

  @classmethod
  def validate_key_type(cls, key_type):
    return key_type in cls.key_type_to_tag_map

  @classmethod
  def get_key_type_from_private_key_tag(cls, private_key_tag):
    for k, v in cls.key_type_to_tag_map.iteritems():
      if v == private_key_tag:
        return k

    raise InvalidKeyTypeException()

  @classmethod
  def public_key_data_to_object(cls, key_type, key_data):
    """Get a PKey object for a given public key type from data
    This is unfortunately a hack around the Paramiko library not giving us a
    good way to represent a generic public key with binary encoding, the
    alternative way to do this would be to have a (fake) host file containing
    one line and hoping the Paramiko code will correctly parses out the key
    type from there"""

    # TODO https://github.com/paramiko/paramiko/issues/663 (everything but
    # rsa currently fails)
    if key_type == RSA_KEY_TYPE:
      return rsakey.RSAKey(data=key_data)
    elif key_type == DSS_KEY_TYPE:
      return dsskey.DSSKey(data=key_data)
    elif key_type == EC_KEY_TYPE:
      return ecdsakey.ECDSAKey(data=key_data)

  @classmethod
  def private_key_data_to_object(cls, key_type, key_data):
    fake_file = cls._get_fake_private_key_file(key_type, key_data)

    if key_type == RSA_KEY_TYPE:
      return rsakey.RSAKey.from_private_key(fake_file)
    elif key_type == DSS_KEY_TYPE:
      return dsskey.DSSKey.from_private_key(fake_file)
    elif key_type == EC_KEY_TYPE:
      return ecdsakey.ECDSAKey.from_private_key(fake_file)

  @classmethod
  def _get_fake_private_key_file(cls, key_type, key_data):
    key_tag = cls.key_type_to_tag_map[key_type]
    prefix = '-----BEGIN ' + key_tag + ' PRIVATE KEY-----'
    body = base64.b64encode(key_data)
    suffix = '-----END ' + key_tag + ' PRIVATE KEY-----'

    return StringIO.StringIO(prefix + '\n' + body + '\n' + suffix)
