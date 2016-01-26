from . import db

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
