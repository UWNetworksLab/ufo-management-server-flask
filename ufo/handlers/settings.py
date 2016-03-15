"""The module for generating and outputing management server settings."""

import json

import flask

import ufo
from ufo.database import models


def _make_settings_json():
  """Generates the json string of all settings based on values in the db.

  Returns:
    A json string of current server settings.
  """
  config = ufo.get_user_config()

  settings_dictionary = {
      "enforce_network_jail": config.network_jail_until_google_auth,
      "enforce_proxy_server_validity": config.proxy_server_validity,
  }

  return json.dumps(settings_dictionary)


def get_settings_resources_dict():
  """Get the resources for the settings configuration component.

    Returns:
      A dict of the resources for the settings configuration component.
  """
  return {
    'hasAddFlow': False,
    'titleText': 'Management Server Settings',
    'getSettingsUrl': flask.url_for('get_settings'),
    'editUrl': flask.url_for('edit_settings'),
    'proxyValidityText': 'Enforce Proxy Server Check from Invitation Link',
    'networkJailText': 'Enforce Network Jail Before Google Login',
    'saveText': 'Save',
  }


@ufo.app.route('/settings/', methods=['GET'])
@ufo.setup_required
def get_settings():
  """Gets the current settings as a json object.

  Returns:
    A flask response with the json settings.
  """
  return flask.Response(_make_settings_json(), mimetype='application/json')


@ufo.app.route('/chromepolicy/edit', methods=['POST'])
@ufo.setup_required
def edit_settings():
  """Receives the posted form for editing the policy config values.

  The new policy config values are stored in the database.

  Returns:
    A redirect back to display chrome policy with will display the new values.
  """
  # TODO(eholder): Move the display of config values and the edit handlers to
  # something more sensible once UI review tells us what that should be. I'm
  # envisioning a settings or options page which is underneath the overall
  # Setup link. For now, I just want these settings to be edittable somewhere.

  config = ufo.get_user_config()

  proxy_server_string = flask.request.form.get('enforce_proxy_server_validity')
  network_jail_string = flask.request.form.get('enforce_network_jail')
  config.proxy_server_validity = json.loads(proxy_server_string)
  config.network_jail_until_google_auth = json.loads(network_jail_string)

  config.save()

  return flask.redirect(flask.url_for('get_settings'))
