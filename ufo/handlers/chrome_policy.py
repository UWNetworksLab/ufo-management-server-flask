"""The module for generating and outputing chrome policy."""

import json

import flask

import ufo
from ufo.database import models
from ufo.handlers import auth


def _make_chrome_policy_json():
  """Generates the json string of chrome policy based on values in the db.

  This policy string has the following form:

  Returns:
    A json string of current chrome policy.
  """
  proxy_servers = models.ProxyServer.query.all()
  proxy_server_dict = {}
  for server in proxy_servers:
    proxy_server_dict[server.ip_address] = (
        server.get_public_key_as_authorization_file_string())
  proxy_server_value_dict = { "Value" : proxy_server_dict }

  config = ufo.get_user_config()
  config_value_dict = { "Value" : config.proxy_server_validity }

  policy_dictionary = {
      "validProxyServers": proxy_server_value_dict,
      "enforceProxyServerValidity": config_value_dict,
  }

  return json.dumps(policy_dictionary)


@ufo.app.route('/chromepolicy/download/', methods=['POST'])
@ufo.setup_required
@auth.login_required
def download_chrome_policy():
  """Outputs the managed chrome policy in json form for downloading as a file.

  Returns:
    A json file of the current managed chrome policy.
  """
  return flask.Response(_make_chrome_policy_json(), headers=ufo.JSON_HEADERS)
