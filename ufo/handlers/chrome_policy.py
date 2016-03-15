"""The module for generating and outputing chrome policy."""

import json

import flask

import ufo
from ufo.database import models


def _make_chrome_policy_json():
  """Generates the json string of chrome policy based on values in the db.

  This policy string has the following form:

  Returns:
    A json string of current chrome policy.
  """
  proxy_servers = models.ProxyServer.query.all()
  proxy_server_public_keys = [s.get_public_key_as_authorization_file_string() for s in proxy_servers]

  config = ufo.get_user_config()

  policy_dictionary = {
      "proxy_server_keys": proxy_server_public_keys,
      "enforce_proxy_server_validity": config.proxy_server_validity,
  }

  return json.dumps(policy_dictionary)


def get_policy_resources_dict():
  """Get the resources for the chrome policy component.

    Returns:
      A dict of the resources for the chrome policy component.
  """
  return {
    'download_chrome_policy': flask.url_for('download_chrome_policy'),
    'isChromePolicy': True,
    'hasAddFlow': False,
    'policy_filename': 'chrome_policy.json',
    'titleText': 'Chrome Policy',
  }


@ufo.app.route('/chromepolicy/')
@ufo.setup_required
def display_chrome_policy():
  """Renders the current chrome policy as json and editable values.

  Returns:
    The rendered chrom_policy.html template with policy values as variables.
  """
  policy_json = _make_chrome_policy_json()
  config = ufo.get_user_config()

  return flask.render_template(
      'chrome_policy.html', policy_json=policy_json,
      enforce_proxy_server_validity=config.proxy_server_validity,
      enforce_network_jail=config.network_jail_until_google_auth)


@ufo.app.route('/chromepolicy/download/')
@ufo.setup_required
def download_chrome_policy():
  """Outputs the managed chrome policy in json form for downloading as a file.

  Returns:
    A json file of the current managed chrome policy.
  """
  return flask.Response(_make_chrome_policy_json(),
                        mimetype='application/json')
