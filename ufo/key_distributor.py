"""The module for distributing user keys to proxy servers."""

from rq import Queue

import ufo
from ufo import models
from ufo import ssh_client
import worker


class KeyDistributor(object):
  """Distributes user keys to proxy servers"""

  def _make_key_string(self):
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
    space = ' '
    endline = '\n'
    for user in users:
      if not user.is_key_revoked:
        user_string = (ssh_starting_portion + space + user.public_key + space +
                       user.email + endline)
        key_string += user_string
  
    return key_string
  
  def _distribute_key(self, proxy_server, key_string):
    """Distributes user keys to the proxy server.
    
    Args:
      proxy_server: db representation of a proxy server.
      key_string: A string of users with associated key.
    """
    client = ssh_client.SSHClient()
    client.connect(proxy_server)
  
    # TODO do stuff
  
    client.close()
  
  def enqueue_key_distribution_jobs(self):
    """Distribute user keys to proxy servers to authenticate invite code."""
    key_string = self._make_key_string()
    proxy_servers = models.ProxyServer.query.all()
    queue = Queue(connection=worker.CONN)
    for proxy_server in proxy_servers:
      queue.enqueue(self._distribute_key, proxy_server, key_string)
