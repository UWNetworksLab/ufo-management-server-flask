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
  proxy_server_dicts = []
  for server in proxy_servers:
    proxy_server_dict = {
        'ip': server.ip_address,
        'public_key': server.get_public_key_as_authorization_file_string(),
    }
    proxy_server_dicts.append(proxy_server_dict)

  config = ufo.get_user_config()

  policy_dictionary = {
      "validProxyServers": proxy_server_dicts,
      "enforceProxyServerValidity": config.proxy_server_validity,
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
    'policyExplanationText': ('Chrome policy is a feature of enterprise Google'
        ' devices which can be used to securely add extra configuration to the'
        ' uProxy frontend. If you use enterprise Google devices through Google'
        ' Apps for Work, you can for example turn on validation for invitation'
        ' links to ensure you are proxying through an endpoint controlled by '
        'the management console.'),
    'policyEditText': ('You can adjust the values below in the Management '
        'Server Settings section and save to update the managed policy json.'
        'Once you are ready, you can click the download link to get your json '
        'policy file generated automatically.'),
    'adminConsoleText': 'Google Admin Console',
    'policyUploadText': ('To push your managed policy out to your devices, '
        'visit Google Admin Console at the link above and navigate to the '
        'uProxy Chrome App/Extension under Device Management -> Chrome '
        'Management -> App Management. For the App and Extension, select the '
        'entry listed, then click User settings. From the list of Orgs, choose'
        ' which you want the policy to apply to, then enable Force '
        'Installation and select Upload Configuration File. Choose the json '
        'file you just downloaded. You may have to click override to edit '
        'Force Installation or Configure\'s values. Finally, click Save.'),
    'downloadText': 'Download',
  }


@ufo.app.route('/chromepolicy/download/')
@ufo.setup_required
@auth.login_required
def download_chrome_policy():
  """Outputs the managed chrome policy in json form for downloading as a file.

  Returns:
    A json file of the current managed chrome policy.
  """
  return flask.Response(_make_chrome_policy_json(),
                        mimetype='application/json')
