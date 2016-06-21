"""Test settings module functionality."""

import json
import unittest

import flask
import mock

import ufo
from ufo import base_test


class SettingsTest(base_test.BaseTest):
  """Test settings functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(SettingsTest, self).setUp()
    super(SettingsTest, self).setup_config()
    super(SettingsTest, self).setup_auth()

  def testGetSettings(self):
    """Test the get settings handler downloads json."""
    resp = self.client.get(flask.url_for('get_settings'))

    json_data = json.loads(resp.data[len(ufo.XSSI_PREFIX):])
    self.assertNotIn('validProxyServers', json_data)
    self.assertIn('enforce_proxy_server_validity', json_data)
    # Uncomment when network jail is available.
    #self.assertIn('enforce_network_jail', json_data)

  def testEditSettings(self):
    """Test posting with modified settings updates in the db."""
    config = ufo.get_user_config()
    initial_proxy_server_config = config.proxy_server_validity
    initial_network_jail_config = config.network_jail_until_google_auth
    data_to_post = {
        'enforce_proxy_server_validity': json.dumps(not initial_proxy_server_config),
        'enforce_network_jail': json.dumps(not initial_network_jail_config),
    }

    resp = self.client.post(flask.url_for('edit_settings'),
                            data=data_to_post, follow_redirects=False)

    updated_config = ufo.get_user_config()
    self.assertEqual(not initial_proxy_server_config,
                     updated_config.proxy_server_validity)
    # Uncomment when network jail is available.
    #self.assertEqual(not initial_network_jail_config,
    #                 updated_config.network_jail_until_google_auth)
    self.assert_redirects(resp, flask.url_for('get_settings'))

if __name__ == '__main__':
  unittest.main()
