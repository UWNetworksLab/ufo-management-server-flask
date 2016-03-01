import base64
import json

from Crypto.PublicKey import RSA
import flask
from mock import MagicMock
from mock import patch

from ufo import base_test
from ufo.database import models
from ufo.handlers import proxy_server


def getBinaryPublicKey(rsakey):
  """Returns the public key as stored in the database."""
  return base64.b64decode(rsakey.publickey().exportKey('OpenSSH').split(' ')[1])

FAKE_PROXY_SERVER_DATA = [
  {'ip_address': '111.111.111.111', 'name': 'fake server 1'},
  {'ip_address': '222:222:222:222', 'name': 'fake server 2'},
  {'ip_address': '333:333:333:333', 'name': 'fake server 3'},
]

for s in FAKE_PROXY_SERVER_DATA:
  key = RSA.generate(1024)
  s['key'] = key
  s['ssh_private_key_type'] = 'ssh-rsa'
  s['ssh_private_key'] = key.exportKey('DER')
  # will not actually correspond in real usage, should not impact tests
  s['host_public_key_type'] = 'ssh-rsa'
  s['host_public_key'] = getBinaryPublicKey(key)

class ProxyServerTest(base_test.BaseTest):
  """Test proxy server class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(ProxyServerTest, self).setUp()
    super(ProxyServerTest, self).setup_config()

  # def testListHandlerRendersTheListTemplate(self):
  #   """Test the list handler gets servers from the database."""
  #   for i in range(len(FAKE_PROXY_SERVER_DATA)):
  #     self._CreateAndSaveFakeProxyServer(i)

  #   resp = self.client.get(flask.url_for('proxyserver_list'))
  #   server_list_output = json.loads(resp.data)['items']

  #   self.assertEquals(len(server_list_output), len(FAKE_PROXY_SERVER_DATA))

  #   for proxy_server_obj in FAKE_PROXY_SERVER_DATA:
  #     self.assertIn(proxy_server._GetViewDataFromProxyServer(proxy_server_obj), server_list_output)

  def testListHandlerRendersResults(self):
    """Test the list proxy server handler gets proxy server from db."""
    for i in range(len(FAKE_PROXY_SERVER_DATA)):
      self._CreateAndSaveFakeProxyServer(i)

    resp = self.client.get(flask.url_for('proxyserver_list'))

    for proxy_server in FAKE_PROXY_SERVER_DATA:
      self.assertTrue(proxy_server['name'] in resp.data)
      self.assertTrue(proxy_server['ip_address'] in resp.data)

  @patch('flask.render_template')
  def testAddProxyServerGetHandler(self, mock_render_template):
    """Test the add proxy server get handler returns the form."""
    mock_render_template.return_value = ''
    resp = self.client.get(flask.url_for('proxyserver_add'))

    args, kwargs = mock_render_template.call_args
    self.assertEquals('proxy_server_form.html', args[0])

  def testAddProxyServer(self):
    """Test the add proxy server post handler inserts the proxy server."""
    fake_server = FAKE_PROXY_SERVER_DATA[0]
    form_data = self._GetProxyServerFormData()
    response = self.client.post(
        flask.url_for('proxyserver_add'),
        data=form_data,
        follow_redirects=False)

    query = models.ProxyServer.query
    query.filter_by(ip_address=fake_server['ip_address'])
    proxy_server_in_db = query.one_or_none()
    self.assertIsNotNone(proxy_server_in_db)
    self.assertEqual(fake_server['name'],
                     proxy_server_in_db.name)
    self.assertEqual(fake_server['key'].exportKey('DER'),
                     proxy_server_in_db.ssh_private_key)
    self.assertEqual(getBinaryPublicKey(fake_server['key']),
                     proxy_server_in_db.host_public_key)

  def testAddingProxyServerRedirectsToList(self):
    """Tests the redirect after adding a proxy server.

    This tests that, after the user adds a proxy server, the user will be
    redirected to the list of proxy servers.
    """
    fake_server = FAKE_PROXY_SERVER_DATA[0]
    data = self._GetProxyServerFormData()

    res = self.client.post(flask.url_for('proxyserver_add'), data=data)

    self.assert_redirects(res, flask.url_for('proxyserver_list'))

  def testEditProxyServerGetHandler(self):
    """Test the edit proxy server get handler returns the form."""
    proxy_server = self._CreateAndSaveFakeProxyServer(0)
    fake_server = FAKE_PROXY_SERVER_DATA[0]

    resp = self.client.get(
        flask.url_for('proxyserver_edit', server_id=proxy_server.id))

    self.assertTrue('proxy-edit-add-form' in resp.data)
    self.assertTrue(fake_server['ip_address'] in resp.data)
    self.assertTrue(fake_server['name'] in resp.data)

  def testEditServerUpdatesKeysInDb(self):
    """Test the edit proxy server post handler saves the edit."""
    proxy_server = self._CreateAndSaveFakeProxyServer(0)

    form_data = self._GetProxyServerFormData(0, 1)
    new_key = FAKE_PROXY_SERVER_DATA[1]['key']

    resp = self.client.post(
        flask.url_for('proxyserver_edit', server_id=proxy_server.id),
        data=form_data)

    self.assertEqual(FAKE_PROXY_SERVER_DATA[0]['name'],
                     proxy_server.name)
    self.assertEqual(FAKE_PROXY_SERVER_DATA[0]['ip_address'],
                     proxy_server.ip_address)
    self.assertEqual(new_key.exportKey('DER'),
                     proxy_server.ssh_private_key)
    self.assertEqual(getBinaryPublicKey(new_key),
                     proxy_server.host_public_key)

  def testEditServerRedirectsToList(self):
    """Tests the redirect after editing a proxy server.

    This tests that, after the user edits a proxy server, the user will be
    redirected to the list of proxy servers.
    """

    proxy_server = self._CreateAndSaveFakeProxyServer(0)

    # we don't actually need to change anything
    form_data = self._GetProxyServerFormData()

    resp = self.client.post(
        flask.url_for('proxyserver_edit', server_id=proxy_server.id),
        data=form_data)

    self.assert_redirects(resp, flask.url_for('proxyserver_list'))

  def testDeleteProxyServerRemovesFromDb(self):
    """Tests the proxy server is actually deleted after the user deletes it."""
    proxy_server = self._CreateAndSaveFakeProxyServer()
    proxy_server_id = proxy_server.id

    response = self.client.get(
        flask.url_for('proxyserver_delete', server_id=proxy_server_id))

    self.assertIsNone(models.ProxyServer.query.get(proxy_server_id))

  def testDeleteProxyServerRedirectsToList(self):
    """Tests the redirect after deleting a proxy server.

    This tests that, after the user deletes a proxy server, the user will be
    redirected to the list of proxy servers.
    """
    proxy_server = self._CreateAndSaveFakeProxyServer()
    proxy_server_id = proxy_server.id

    response = self.client.get(
        flask.url_for('proxyserver_delete', server_id=proxy_server_id))
    self.assert_redirects(response, flask.url_for('proxyserver_list'))

  def _GetProxyServerFormData(self, id_id=0, key_id=0):
    server = FAKE_PROXY_SERVER_DATA[id_id]
    key = FAKE_PROXY_SERVER_DATA[key_id]['key']
    return {
      'name': server['name'],
      'ip_address': server['ip_address'],
      'private_key': key.exportKey(),
      'public_key': key.publickey().exportKey('OpenSSH'),
    }

  def _CreateAndSaveFakeProxyServer(self, i=0):
    """Create a fake proxy server, and save it into db."""
    proxy_server = models.ProxyServer(
        ip_address=FAKE_PROXY_SERVER_DATA[i]['ip_address'],
        name=FAKE_PROXY_SERVER_DATA[i]['name'],
        ssh_private_key=FAKE_PROXY_SERVER_DATA[i]['ssh_private_key'],
        ssh_private_key_type=FAKE_PROXY_SERVER_DATA[i]['ssh_private_key_type'],
        host_public_key=FAKE_PROXY_SERVER_DATA[i]['host_public_key'],
        host_public_key_type=FAKE_PROXY_SERVER_DATA[i]['host_public_key_type'])

    return proxy_server.save()

if __name__ == '__main__':
  unittest.main()
