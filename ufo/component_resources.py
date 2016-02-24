"""This module holds the resources for the various components."""

import flask


def _get_user_resources_dict():
  """Get the resources for the user component.

    Returns:
      A dict of the resources for the user component.
  """
  return {
    'addUrl': flask.url_for('add_user'),
    'addIconUrl': flask.url_for('static', filename='add-users.svg'),
    'addText': 'Add Users',
    'listUrl': flask.url_for('user_list'),
    'titleText': 'Users',
    'itemIconUrl': flask.url_for('static', filename='user.svg'),
    'isUser': True,
  }

def _get_proxy_resources_dict():
  """Get the resources for the proxy server component.

    Returns:
      A dict of the resources for the proxy server component.
  """
  return {
    'addUrl': flask.url_for('proxyserver_add'),
    'addIconUrl': flask.url_for('static', filename='add-servers.svg'),
    'addText': 'Add a Server',
    'listUrl': flask.url_for('proxyserver_list'),
    'titleText': 'Servers',
    'itemIconUrl': flask.url_for('static', filename='server.svg'),
    'isProxyServer': True,
  }

def _get_policy_resources_dict():
  """Get the resources for the chrome policy component.

    Returns:
      A dict of the resources for the chrome policy component.
  """
  return {
    'download_chrome_policy': flask.url_for('download_chrome_policy'),
    'isChromePolicy': True,
    'policy_filename': 'chrome_policy.json',
    'titleText': 'Chrome Policy',
  }
