"""Test chrome policy module functionality."""

import json
import unittest

import flask
import mock

import ufo
from ufo import base_test


class ChromePolicyTest(base_test.BaseTest):
  """Test chrome policy functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(ChromePolicyTest, self).setUp()
    super(ChromePolicyTest, self).setup_config()
    super(ChromePolicyTest, self).setup_auth()

  def testChromePolicyDownload(self):
    """Test the chrome policy download handler downloads policy json."""
    resp = self.client.post(flask.url_for('download_chrome_policy'))
    json_data = json.loads(resp.data)

    proxy_servers = json_data.get('validProxyServers')
    self.assertIsNotNone(proxy_servers)
    self.assertIsNotNone(proxy_servers.get('Value'))

    enforce_validity = json_data.get('enforceProxyServerValidity')
    self.assertIsNotNone(enforce_validity)
    self.assertIsNotNone(enforce_validity.get('Value'))

    self.assertNotIn('enforce_network_jail', json_data)

if __name__ == '__main__':
  unittest.main()
