import base64

from . import db

from Crypto.PublicKey import RSA

LONG_STRING_LENGTH = 1024

class Model(db.Model):
  __abstract__ = True

  @classmethod
  def GetAll(cls):
    return cls.query.all()

  @classmethod
  def GetById(cls, id):
    return cls.query.get(id)

  def Add(self):
    db.session.add(self)
    db.session.commit()

    return self

  def Delete(self):
    db.session.delete(self)
    db.session.commit()


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

  def __init__(self):
    self.regenerate_key_pair()

  @staticmethod
  def _GenerateKeyPair():
    """Generate a private and public key pair in base64.

    Returns:
      key_pair: A dictionary with private_key and public_key in b64 value.
    """
    rsa_key = RSA.generate(2048)
    private_key = base64.urlsafe_b64encode(rsa_key.exportKey())
    public_key = base64.urlsafe_b64encode(rsa_key.publickey().exportKey())

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
  ssh_private_key = db.Column(db.String(LONG_STRING_LENGTH))
  fingerprint = db.Column(db.String(LONG_STRING_LENGTH))

  def __init__(self, ip_address, name, ssh_private_key, fingerprint):
    self.ip_address=ip_address
    self.name = name
    self.ssh_private_key = ssh_private_key
    self.fingerprint = fingerprint
