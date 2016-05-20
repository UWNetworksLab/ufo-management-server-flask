import StringIO

import bcrypt
from Crypto.PublicKey import RSA
from paramiko import hostkeys
from paramiko import pkey
import sqlalchemy

import ufo
from ufo.services import custom_exceptions
from ufo.services import ssh_client

LONG_STRING_LENGTH = 1024
REVOKED_TEXT = 'Access Disabled'
NOT_REVOKED_TEXT = 'Access Enabled'
DISABLE_TEXT = 'Disable'
ENABLE_TEXT = 'Enable'
# Since we aren't using pypi, I don't think I have access to real enums.
# We can add support using enum34 and pypi if we ever choose, but this method
# using a dictionary should be sufficient until that time.
# TODO(eholder): Follow up on whether to convert to pypi for real enums. See
# here for more info: http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
CRON_JOB_ACTIONS = {
  'nothing': 'nothing',
  'revoke': 'revoke',
  'delete': 'delete',
}


class Model(ufo.db.Model):
  """Helpful functions for the database models

  Most method implementations are taken from
  https://github.com/sloria/cookiecutter-flask"""
  __abstract__ = True
  id = ufo.db.Column(ufo.db.Integer, primary_key=True)

  def update(self, commit=True, **kwargs):
    """Update the given entity by setting the given attributes and saving.

    Args:
      commit: A boolean for whether or not to commit the result immediately.
      **kwargs: Any additional arguments for the attributes on the entity.

    Returns:
      The result of saving the new entity.
    """
    for attr, value in kwargs.items():
      setattr(self, attr, value)
    return commit and self.save() or self

  def save(self, commit=True):
    """Add the given entity and save if specified.

    Args:
      commit: A boolean for whether or not to commit the result immediately.

    Returns:
      The specified entity.

    Raises:
      custom_exceptions.UnableToSaveToDB: If there is an integrity error from
                                          attempting to save an item which
                                          duplicates a unique value.
    """
    ufo.db.session.add(self)
    if commit:
      try:
        ufo.db.session.commit()
      except sqlalchemy.exc.IntegrityError:
        ufo.app.logger.error(
          'Unable to save to database.  Check if constraint is violated.')
        ufo.db.session.rollback()
        raise custom_exceptions.UnableToSaveToDB
    return self

  def delete(self, commit=True):
    """Delete the given entity and save if specified.

    Args:
      commit: A boolean for whether or not to commit the result immediately.

    Returns:
      The result of committing the given entity if specified or False.
    """
    ufo.db.session.delete(self)
    return commit and ufo.db.session.commit()

  def to_dict(self):
    """Generate a dictionary representation of the given entity.

    This method does nothing on the base model class, but will be implemented
    for each child class.

    Returns:
      An empty dictionary for this class.
    """
    return {}

  @classmethod
  def get_items_as_list_of_dict(cls):
    """Retrieves a list of all the entities of this class in dictionary form.

    Returns:
      A list of entities in dictionary form from the database.
    """
    return cls.make_items_into_list_of_dict(cls.query.order_by(cls.id).all())

  @classmethod
  def search(cls, search_text):
    """Retrieves a list of the entities matching the search string.

    This uses whoosh_search from the whoosh alchemy flask extension.

    Args:
      search_text: A string of the text to search for in the db.

    Returns:
      A list of entities in dictionary form matching the search string.
    """
    items = cls.query.whoosh_search(search_text, or_=True).all()
    return cls.make_items_into_list_of_dict(items)

  @classmethod
  def make_items_into_list_of_dict(cls, items):
    """Transforms a list of entities into a list of their dictionary form.

    Args:
      items: The entities in the database to transform.

    Returns:
      A list of the given entities in dictionary form.
    """
    to_return = []
    for item in items:
      to_return.append(item.to_dict())
    return to_return


class Config(Model):
  """Class for anything that needs to be stored as a singleton for the site
  configuration
  """
  __tablename__ = 'config'
  __searchable__ = []

  id = ufo.db.Column(ufo.db.Integer, primary_key=True)

  isConfigured = ufo.db.Column(ufo.db.Boolean(), default=False)

  credentials = ufo.db.Column(ufo.db.Text())
  domain = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH))
  dv_content = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH))
  proxy_server_validity = ufo.db.Column(ufo.db.Boolean(), default=False)
  network_jail_until_google_auth = ufo.db.Column(ufo.db.Boolean(),
                                                 default=False)
  user_revoke_action = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH),
                                     default=CRON_JOB_ACTIONS['revoke'])
  user_delete_action = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH),
                                     default=CRON_JOB_ACTIONS['delete'])
  user_unrevoke_action = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH),
                                       default=CRON_JOB_ACTIONS['nothing'])
  user_undelete_action = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH),
                                       default=CRON_JOB_ACTIONS['nothing'])

  def to_dict(self):
    """Get the config as a dict.

      Returns: A dictionary of the config.
    """
    return {
      'is_configured': self.isConfigured,
      'credentials': self.credentials,
      'domain': self.domain,
      'dv_content': self.dv_content,
      'proxy_server_validity': self.proxy_server_validity,
      'network_jail_until_google_auth': self.network_jail_until_google_auth,
    }


class User(Model):
  """Class for information about the users of the proxy servers."""
  __tablename__ = "user"
  __searchable__ = ['email', 'name', 'domain']

  id = ufo.db.Column(ufo.db.Integer, primary_key=True)

  email = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH), unique=True)
  name = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH))
  private_key = ufo.db.Column(ufo.db.LargeBinary())
  public_key = ufo.db.Column(ufo.db.LargeBinary())
  is_key_revoked = ufo.db.Column(ufo.db.Boolean(), default=False)
  domain = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH))
  did_cron_revoke = ufo.db.Column(ufo.db.Boolean(), default=False)

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
    """Call generate key pair and set the new key pair on the user."""
    key_pair = User._GenerateKeyPair()
    self.private_key = key_pair['private_key']
    self.public_key = key_pair['public_key']

  def to_dict(self):
    """Get the user as a dictionary.

      Returns:
        A dictionary of the user.
    """
    return {
      "id": self.id,
      'email': self.email,
      'name': self.name,
      'private_key': self.private_key,
      'public_key': self.public_key,
      'access': REVOKED_TEXT if self.is_key_revoked else NOT_REVOKED_TEXT,
      'accessChange': ENABLE_TEXT if self.is_key_revoked else DISABLE_TEXT,
    }


class ProxyServer(Model):
  """Class for information about the proxy servers.

  The ssh_private_key is the private key that can access the proxy server
  as root via ssh.  This is used by the ssh client to access
  the proxy server to distribute user keys.

  The host_public_key is the public key of the proxy server as can be found in
  /etc/ssh/ssh_host_rsa_key.pub file.  This is used to authenticate
  the proxy server.
  """
  __tablename__ = "proxyserver"
  __searchable__ = ['ip_address', 'name']

  id = ufo.db.Column(ufo.db.Integer, primary_key=True)

  ip_address = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH), unique=True)
  name = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH))
  ssh_private_key = ufo.db.Column(ufo.db.LargeBinary())
  ssh_private_key_type = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH))
  host_public_key = ufo.db.Column(ufo.db.LargeBinary())
  host_public_key_type = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH))

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

  def to_dict(self):
    """Get the proxy server as a dictionary.

      Returns:
        A dictionary of the proxy server.
    """
    private_key = ssh_client.SSHClient.private_key_data_to_object(
        self.ssh_private_key_type,
        self.ssh_private_key)
    private_key_file = StringIO.StringIO()
    private_key.write_private_key(private_key_file)
    private_key_text = private_key_file.getvalue()

    return {
      "id": self.id,
      "name": self.name,
      "ip_address": self.ip_address,
      "host_public_key": self.get_public_key_as_authorization_file_string(),
      "ssh_private_key": private_key_text,
      }


class AdminUser(Model):
  """People who have access to the management server, as in admins."""
  __tablename__ = "admin_user"
  __searchable__ = ['email']

  id = ufo.db.Column(ufo.db.Integer, primary_key=True)

  email = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH), index=True,
                        unique=True)
  password = ufo.db.Column(ufo.db.String(LONG_STRING_LENGTH))

  @classmethod
  def get_by_email(cls, email):
    """Lookup an admin user by email.

    Agrs:
      email: The email to search for an admin user by.

    Returns:
      The specified admin user or None if not found.
    """
    return cls.query.filter_by(email=email).one_or_none()

  def set_password(self, password):
    """Sets the password on a given admin user.

    Args:
      password: The new password to set on the admin user.
    """
    self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

  def does_password_match(self, password):
    """Checks if the given password matches the given admin user.

    Agrs:
      password: The password to check an admin user by.

    Returns:
      True if the password matches the admin user and False otherwise.
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), self.password.encode('utf-8'))
    return hashed == self.password

  def delete(self, commit=True):
    """Delete the given entity and save if specified.

    The admin specific implementation here will raise an exception if this is
    the last remaining admin that is being deleted.

    Args:
      commit: A boolean for whether or not to commit the result immediately.

    Returns:
      The result of committing the given entity if specified or False.

    Raises:
      custom_exceptions.AttemptToRemoveLastAdmin: If this is the only admin in
                                                  the database.
    """
    if len(AdminUser.query.all()) == 1:
      raise custom_exceptions.AttemptToRemoveLastAdmin

    super(AdminUser, self).delete(commit)

  def to_dict(self):
    """Get the admin user as a dictionary.

      Returns:
        A dictionary of the admin user.
    """
    return {
      "id": self.id,
      "email": self.email,
    }

