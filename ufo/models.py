from . import db

from Crypto.PublicKey import RSA

LONG_STRING_LENGTH = 1024

class Config(db.Model):
  """Class for anything that needs to be stored as a singleton for the site
  configuration
  """
  __tablename__ = 'config'

  id = db.Column(db.Integer, primary_key=True)

  isConfigured = db.Column(db.Boolean(), default=False)

  credentials = db.Column(db.Text())
  domain = db.Column(db.String(LONG_STRING_LENGTH))
  dv_content = db.Column(db.String(LONG_STRING_LENGTH))


class User(db.Model):
  """Class for information about the users of the proxy servers
  """
  __tablename__ = "user"

  id = db.Column(db.Integer, primary_key=True)

  email = db.Column(db.String(LONG_STRING_LENGTH))
  name = db.Column(db.String(LONG_STRING_LENGTH))
  private_key = db.Column(db.LargeBinary())
  public_key = db.Column(db.LargeBinary())
  is_key_revoked = db.Column(db.Boolean(), default=False)

  def __init__(self):
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

class ProxyServer(db.Model):
  """Class for information about the proxy servers
  """
  __tablename__ = "proxyserver"

  id = db.Column(db.Integer, primary_key=True)

  ip_address = db.Column(db.String(LONG_STRING_LENGTH))
  name = db.Column(db.String(LONG_STRING_LENGTH))
  ssh_private_key = db.Column(db.String(LONG_STRING_LENGTH))
  fingerprint = db.Column(db.String(LONG_STRING_LENGTH))
