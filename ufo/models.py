from . import db

import bcrypt
from Crypto.PublicKey import RSA
from paramiko import hostkeys
from paramiko import pkey
import StringIO
import ssh_client

LONG_STRING_LENGTH = 1024

class Model(db.Model):
  """Helpful functions for the database models

  Most method implementations are taken from
  https://github.com/sloria/cookiecutter-flask"""
  __abstract__ = True

  def update(self, commit=True, **kwargs):
    for attr, value in kwargs.items():
      setattr(self, attr, value)
    return commit and self.save() or self

  def save(self, commit=True):
    db.session.add(self)
    if commit:
      db.session.commit()
    return self

  def delete(self, commit=True):
    db.session.delete(self)
    return commit and db.session.commit()


class Config(Model):
  """Class for anything that needs to be stored as a singleton for the site
  configuration
  """
  __tablename__ = 'config'

  id = db.Column(db.Integer, primary_key=True)

  isConfigured = db.Column(db.Boolean(), default=False)

  credentials = db.Column(db.Text())
  domain = db.Column(db.String(LONG_STRING_LENGTH))
  dv_content = db.Column(db.String(LONG_STRING_LENGTH))
  proxy_server_validity = db.Column(db.Boolean(), default=False)
  network_jail_until_google_auth = db.Column(db.Boolean(), default=False)


class User(Model):
  """Class for information about the users of the proxy servers
  """
  __tablename__ = "user"

  id = db.Column(db.Integer, primary_key=True)

  email = db.Column(db.String(LONG_STRING_LENGTH))
  name = db.Column(db.String(LONG_STRING_LENGTH))
  private_key = db.Column(db.LargeBinary())
  public_key = db.Column(db.LargeBinary())
  is_key_revoked = db.Column(db.Boolean(), default=False)

  def __init__(self, **kwargs):
    super(User, self).__init__(**kwargs)

    self.regenerate_key_pair()

  @staticmethod
  def _GenerateKeyPair():
    """Generate a private and public key pair in base64.

    Returns:
      key_pair: A dictionary with private_key and public_key in b64 value.
    """
    rsa_key = RSA.generate(2048)
    private_key = rsa_key.exportKey()
    public_key = rsa_key.publickey().exportKey()

    return {
        'private_key': private_key,
        'public_key': public_key
    }

  def regenerate_key_pair(self):
    key_pair = User._GenerateKeyPair()
    self.private_key = key_pair['private_key']
    self.public_key = key_pair['public_key']


class ProxyServer(Model):
  """Class for information about the proxy servers
  """
  __tablename__ = "proxyserver"

  id = db.Column(db.Integer, primary_key=True)

  ip_address = db.Column(db.String(LONG_STRING_LENGTH))
  name = db.Column(db.String(LONG_STRING_LENGTH))
  ssh_private_key = db.Column(db.LargeBinary())
  ssh_private_key_type = db.Column(db.String(LONG_STRING_LENGTH))
  host_public_key = db.Column(db.LargeBinary())
  host_public_key_type = db.Column(db.String(LONG_STRING_LENGTH))

  def read_private_key_from_file_contents(self, contents):
    pkey_instance = pkey.PKey()
    for key_type, key_tag in ssh_client.SSHClient.key_type_to_tag_map.iteritems():
      if ('BEGIN ' + key_tag + ' PRIVATE KEY') not in contents:
        continue

      # Using the private implementation is, unfortunately, the best way to
      # handle this.  If there are ever concerns about this, we can always
      # write a simplified parser
      self.ssh_private_key = pkey_instance._read_private_key(
          key_tag,
          StringIO.StringIO(contents))
      self.ssh_private_key_type = key_type

      return

    raise Exception("Unrecognized private key file")

  def read_public_key_from_file_contents(self, contents):
    try:
      # this should be from a public key file which will not contain the actual
      # host part of the "line"
      host_key_entry = hostkeys.HostKeyEntry.from_line('0.0.0.0 ' + contents)
    except:
      # might be passing in a line from a host file
      host_key_entry = hostkeys.HostKeyEntry.from_line(contents)

    self.host_public_key_type = host_key_entry.key.get_name()
    self.host_public_key = host_key_entry.key.asbytes()

  def get_public_key_as_authorization_file_string(self):
    """Creates an output-able string of the public key for the server.

    Returns:
      A string of the public key for this proxy server.
    """
    public_key = ssh_client.SSHClient.public_key_data_to_object(
        self.host_public_key_type,
        self.host_public_key)
    return public_key.get_name() + ' ' + public_key.get_base64()


class ManagementServerUser(Model):
  """People who have access to the management server
  """
  __tablename__ = "management_server_user"

  id = db.Column(db.Integer, primary_key=True)

  username = db.Column(db.String(LONG_STRING_LENGTH), index=True, unique=True)
  password = db.Column(db.String(LONG_STRING_LENGTH))

  @classmethod
  def get_by_username(cls, username):
    return cls.query.filter_by(username=username).one_or_none()

  def set_password(self, password):
    self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

  def check_password(self, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), self.password.encode('utf-8'))
    return hashed == self.password
