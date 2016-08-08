"""The module for distributing user keys to proxy servers."""

from Crypto.PublicKey import RSA
import pipes
import string

import ufo
from ufo.database import models
from ufo.services import ssh_client


class KeyDistributor(object):
  """Distributes user keys to proxy servers"""

  # VisibleForTesting
  def make_key_string(self):
    """Generate the key string in open ssh format for pushing to proxy servers.
    This key string includes only the public key for each user in order to grant
    the user access to each proxy server.
    Returns:
      key_string: A string of users with associated key.
    """
    # TODO: Improve this so that we only do this if there are relevant changes.
    users = models.User.get_unrevoked_users()
    key_string = ''
    ssh_starting_portion = 'command="/login.sh",permitopen="zork:9000",no-agent-forwarding,no-pty,no-user-rc,no-X11-forwarding'
    endline = '\n'
    for user in users:

      public_key = RSA.importKey(user.public_key)
      public_key_string = public_key.exportKey('OpenSSH')

      # Do not include email at the end of the user_string as it's a security
      # hole.  It's also just a comment without any specific use.
      # If really necessary, encode special characters with something like json.
      user_string = (ssh_starting_portion + ' ' + public_key_string + ' ' +
                     endline)
      key_string += user_string

    return key_string

  def _distribute_key(self, proxy_server, key_string):
    """Distributes user keys to the proxy server.
    Args:
      proxy_server: db representation of a proxy server.
      key_string: A string of users with associated key.
    """
    ufo.app.logger.info('Distributing keys to proxy server: %s',
                        proxy_server.name)
    client = ssh_client.SSHClient()

    try:
      client.connect(proxy_server)
    except (ssh_client.SSHConnectionException,
            ssh_client.InvalidKeyTypeException):
      ufo.app.logger.error(
          'Unable to connect to proxy server %s to distribute keys.',
          proxy_server.name)
      # TODO: Notify admin in some way, that the keys distribution have error.
      return

    key_string = pipes.quote(key_string)  # Prevent shell injection.
    data = {
        'key_string': key_string,
        'tmp_file_path': '/tmp/ufo-keys',
        'authorized_keys_path': '/home/getter/.ssh/authorized_keys',
        'container_name': 'uproxy-sshd',
        'getter_user': 'getter',
        'getter_group': 'getter',
    }
    # '>' will overwrite existing file, versus '>>' which will append

    make_file = "echo {key_string} > {tmp_file_path}".format(**data)
    copy_file = "docker cp {tmp_file_path} {container_name}:{authorized_keys_path}".format(**data)
    mod_file = "docker exec {container_name} chmod 644 {authorized_keys_path}".format(**data)
    own_file = "docker exec {container_name} chown {getter_user}:{getter_group} /home/getter/.ssh/authorized_keys".format(**data)
    cleanup = "rm -f {tmp_file_path}".format(**data)
    command = string.join([make_file, copy_file, mod_file, own_file, cleanup], ' && ')
    stdin, stdout, stderr = client.exec_command(command)

    error = stderr.readlines()
    if error:
      ufo.app.logger.error('Error when saving keys on proxy server: %s, %s',
                           proxy_server.name, error)
      # TODO: Notify admin in some way, that the keys distribution have error.
    else:
      ufo.app.logger.info('Successfully distributed keys to proxy server: %s',
                          proxy_server.name)

    client.close()

  def start_key_distribution(self):
    """Start distributing user keys to all proxy servers."""
    ufo.app.logger.info('Start key distribution.')
    key_string = self.make_key_string()
    proxy_servers = models.ProxyServer.query.all()
    for proxy_server in proxy_servers:
      self._distribute_key(proxy_server, key_string)
