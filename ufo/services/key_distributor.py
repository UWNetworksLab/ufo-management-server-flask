"""The module for distributing user keys to proxy servers."""

from rq import Queue

import ufo
from ufo import app
from ufo.database import models
from ufo.services import ssh_client
import worker


# This is the target which the key strings should be saved on the proxy server.
KEY_FILENAME = '/tmp/change_me.txt'


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
    users = models.User.query.all()
    key_string = ''
    ssh_starting_portion = 'ssh-rsa'
    endline = '\n'
    for user in users:
      if not user.is_key_revoked:
        user_string = (ssh_starting_portion + ' ' + user.public_key + ' ' +
                       user.email + endline)
        key_string += user_string

    return key_string

  def _distribute_key(self, proxy_server, key_string):
    """Distributes user keys to the proxy server.
    Args:
      proxy_server: db representation of a proxy server.
      key_string: A string of users with associated key.
    """
    app.logger.info('Distributing keys to proxy server: %s', proxy_server.name)
    client = ssh_client.SSHClient()

    try:
      client.connect(proxy_server)
    except (ssh_client.SSHConnectionException, 
            ssh_client.InvalidKeyTypeException):
      app.logger.error(
          'Unable to connect to proxy server %s to distribute keys.',
          proxy_server.name)
      # TODO: Notify admin in some way, that the keys distribution have error.
      return

    # TODO: Change to the actual file when we know where and what it should be.
    data = {
        'key_string': key_string,
        'key_filename': KEY_FILENAME
    }
    # '>' will overwrite existing file, versus '>>' which will append
    create_new_key_file = "echo '{key_string}' > {key_filename}".format(**data)
    stdin, stdout, stderr = client.exec_command(create_new_key_file)

    error = stderr.readlines()
    if error:
      app.logger.error('Error when saving keys on proxy server: %s, %s',
                      proxy_server.name, error)
      # TODO: Notify admin in some way, that the keys distribution have error.
    else:
      app.logger.info('Successfully distributed keys to proxy server: %s',
                      proxy_server.name)

    client.close()

  def enqueue_key_distribution_jobs(self):
    """Distribute user keys to proxy servers to authenticate invite code."""
    app.logger.info('Enqueuing key distribution jobs.')
    key_string = self.make_key_string()
    proxy_servers = models.ProxyServer.query.all()
    queue = Queue(connection=worker.CONN)
    for proxy_server in proxy_servers:
      queue.enqueue(self._distribute_key, proxy_server, key_string)
