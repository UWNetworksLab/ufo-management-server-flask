"""The module for generating and outputing chrome policy."""

from . import app, setup_required

import flask
import json

import ufo.models


def _make_chrome_policy_json():
  """Generates the json string of chrome policy based on values in the db.

  This policy string has the following form:

  Returns:
    A json string of current chrome policy.
  """
  proxy_servers = ufo.models.ProxyServer.query.all()
  proxy_server_public_keys = [s.make_public_key() for s in proxy_servers]

  config = ufo.models.Config.query.get(0)

  policy_dictionary = {
      "proxy_server_keys": proxy_server_public_keys,
      "enforce_proxy_server_validity": config.proxy_server_validity,
      "enforce_network_jail": config.network_jail_until_google_auth,
  }

  return json.dumps(policy_dictionary)


@app.route('/chromepolicy/')
@setup_required
def display_chrome_policy():
  """Renders the current chrome policy as json and editable values.

  Returns:
    The rendered chrom_policy.html template with policy values as variables.
  """
  policy_json = _make_chrome_policy_json()
  config = ufo.models.Config.query.get(0)

  return flask.render_template(
      'chrome_policy.html', policy_json=policy_json,
      enforce_proxy_server_validity=config.proxy_server_validity,
      enforce_network_jail=config.network_jail_until_google_auth)


@app.route('/chromepolicy/download/')
@setup_required
def download_chrome_policy():
  """Outputs the managed chrome policy in json form for downloading as a file.

  Returns:
    A json file of the current managed chrome policy.
  """
  return _make_chrome_policy_json()

@app.route('/chromepolicy/edit', methods=['POST'])
@setup_required
def edit_policy_config():
  """Receives the posted form for editing the policy config values.

  The new policy config values are stored in the database.

  Returns:
    A redirect back to display chrome policy with will display the new values.
  """

  config = ufo.models.Config.query.get(0)

  # TODO(eholder): The Polymer html for sending toggle button values as inputs
  # really sucks. I basically have to parse it out manually in JS then set it
  # to a hidden input value. If we used iron-form, that may help with setting
  # those as inputs on its own. That introduces a problem with refreshing the
  # page on response or writing the response back into the UI for an update...
  # TODO(eholder): There has to be a better way to convert strings to bools...
  proxy_server_string = flask.request.form.get('enforce_proxy_server_validity')
  network_jail_string = flask.request.form.get('enforce_network_jail')

  config.proxy_server_validity = (proxy_server_string == 'true' or
                                  proxy_server_string == 'True')
  config.network_jail_until_google_auth = (network_jail_string == 'true' or
                                           network_jail_string == 'True')

  config.save()

  return flask.redirect(flask.url_for('display_chrome_policy'))
