
import flask
import json
import mock

import base_test
import models
import chrome_policy

class ChromePolicyTest(base_test.BaseTest):
  """Test chrome policy functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(ChromePolicyTest, self).setUp()
    super(ChromePolicyTest, self).setup_config()

  @mock.patch('flask.render_template')
  def testChromePolicyRenderTemplate(self, mock_render_template):
    """Test the chrome policy handler renders the page."""
    mock_render_template.return_value = ''
    resp = self.client.get(flask.url_for('chrome_policy'))

    args, kwargs = mock_render_template.call_args
    self.assertEquals('chrome_policy.html', args[0])
    json_data = json.loads(kwargs['policy_json'])
    self.assertIn('proxy_server_keys', json_data)
    self.assertIn('enforce_proxy_server_validity', json_data)
    self.assertIn('enforce_network_jail', json_data)

  def testChromePolicyDownload(self):
    """Test the chrome policy download handler downloads json."""
    resp = self.client.get(flask.url_for('chrome_policy_download'))

    json_data = json.loads(resp.data)
    self.assertIn('proxy_server_keys', json_data)
    self.assertIn('enforce_proxy_server_validity', json_data)
    self.assertIn('enforce_network_jail', json_data)

if __name__ == '__main__':
  unittest.main()
