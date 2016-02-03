"""The module for generating and outputing chrome policy."""

from . import app, setup_required

import flask
import json

import models


def _MakeChromePolicyJson():
  """Generate the json string of chrome policy based on values in the database.

  This policy string has the following form:

  Returns:
    A json string of current chrome policy.
  """
  proxy_servers = models.ProxyServer.query.all()
  proxy_server_public_keys = [s._MakePublicKey() for s in proxy_servers]

  config = models.Config.query.get(0)

  policy_dictionary = {
      "proxy_server_keys": proxy_server_public_keys,
      "enforce_proxy_server_validity": config.proxy_server_validity,
      "enforce_network_jail": config.network_jail_until_google_auth,
  }

  return json.dumps(policy_dictionary)


@app.route('/chromepolicy/')
@setup_required
def chrome_policy():
  policy_json = _MakeChromePolicyJson()

  return flask.render_template('chrome_policy.html', policy_json=policy_json)


@app.route('/chromepolicy/download/')
@setup_required
def chrome_policy_download():
  return _MakeChromePolicyJson()
