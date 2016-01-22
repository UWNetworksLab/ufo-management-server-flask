from mock import MagicMock
from mock import patch

import flask

import base_test
import models
import proxy_server


FAKE_PROXY_SERVER_DATA = [
  {'ip_address': '111.111.111.111', 'name': 'fake server 1', 
   'ssh_private_key': '11111', 'fingerprint': '11:11:11:11'},
  {'ip_address': '222:222:222:222', 'name': 'fake server 2', 
   'ssh_private_key': '22222', 'fingerprint': '22:22:22:22'},
  {'ip_address': '333:333:333:333', 'name': 'fake server 3', 
   'ssh_private_key': '33333', 'fingerprint': '33:33:33:33'},
]

FAKE_ID = 1000
FAKE_MODEL_PROXY_SERVER = MagicMock(
    id=FAKE_ID,
    ip_address=FAKE_PROXY_SERVER_DATA[0]['ip_address'],
    ssh_private_key=FAKE_PROXY_SERVER_DATA[0]['ssh_private_key'],
    fingerprint=FAKE_PROXY_SERVER_DATA[0]['fingerprint'])
FAKE_MODEL_PROXY_SERVER.name = FAKE_PROXY_SERVER_DATA[0]['name']


class ProxyServerTest(base_test.BaseTest):
  """Test proxy server class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(ProxyServerTest, self).setUp()
    super(ProxyServerTest, self).setup_config()

  def testListProxyServerHandler(self):
    """Test the list proxy server handler displays proxy server from db."""
    proxy_servers = []

    for fake_proxy_server_data in FAKE_PROXY_SERVER_DATA:
      proxy_server = models.ProxyServer(
          ip_address=fake_proxy_server_data['ip_address'],
          name=fake_proxy_server_data['name'],
          ssh_private_key=fake_proxy_server_data['ip_address'],
          fingerprint=fake_proxy_server_data['fingerprint'])
      proxy_server.save()
      proxy_servers.append(proxy_server)

    resp = self.client.get(flask.url_for('proxyserver_list'))

    for proxy_server in proxy_servers:
      self.assertTrue(proxy_server.name in resp.data)
      self.assertTrue(proxy_server.ip_address in resp.data)
      self.assertTrue(proxy_server.ssh_private_key in resp.data)
      self.assertTrue(proxy_server.fingerprint in resp.data)

  @patch('flask.render_template')
  def testAddProxyServerGetHandler(self, mock_render_template):
    """Test the add proxy server get handler returns the form."""
    mock_render_template.return_value = ''
    resp = self.client.get(flask.url_for('proxyserver_add'))

    args, kwargs = mock_render_template.call_args
    self.assertEquals('proxy_server_form.html', args[0])

  def testAddProxyServer(self):
    """Test the add proxy server post handler inserts the proxy server."""
    form_data = {
      'ip_address': FAKE_PROXY_SERVER_DATA[0]['ip_address'],
      'name': FAKE_PROXY_SERVER_DATA[0]['name'],
      'ssh_private_key': FAKE_PROXY_SERVER_DATA[0]['ssh_private_key'],
      'fingerprint': FAKE_PROXY_SERVER_DATA[0]['fingerprint']
    }
    response = self.client.post(
        flask.url_for('proxyserver_add'),
        data=form_data,
        follow_redirects=False)

    query = models.ProxyServer.query
    query.filter_by(ip_address=FAKE_PROXY_SERVER_DATA[0]['ip_address'])
    proxy_server_in_db = query.one_or_none()
    self.assertEqual(FAKE_PROXY_SERVER_DATA[0]['name'],
                     proxy_server_in_db.name)
    self.assertEqual(FAKE_PROXY_SERVER_DATA[0]['ip_address'],
                     proxy_server_in_db.ip_address)
    self.assertEqual(FAKE_PROXY_SERVER_DATA[0]['ssh_private_key'],
                     proxy_server_in_db.ssh_private_key)
    self.assertEqual(FAKE_PROXY_SERVER_DATA[0]['fingerprint'],
                     proxy_server_in_db.fingerprint)

    self.assert_redirects(response, flask.url_for('proxyserver_list'))

  def testEditProxyServerGetHandler(self):
    """Test the edit proxy server get handler returns the form."""
    proxy_server = self._CreateAndSaveFakeProxyServer()

    query = models.ProxyServer.query
    query.filter_by(ip_address=FAKE_PROXY_SERVER_DATA[0]['ip_address'])
    proxy_server_in_db = query.one_or_none()
    resp = self.client.get(
        flask.url_for('proxyserver_edit', server_id=proxy_server_in_db.id))

    self.assertTrue('proxy-edit-add-form' in resp.data)
    self.assertTrue(proxy_server.ip_address in resp.data)
    self.assertTrue(proxy_server.name in resp.data)
    self.assertTrue(proxy_server.ssh_private_key in resp.data)
    self.assertTrue(proxy_server.fingerprint in resp.data)

  def testEditProxyServerPostHandler(self):
    """Test the edit proxy server post handler saves the edit."""
    proxy_server = self._CreateAndSaveFakeProxyServer()

    updated_proxy_server = models.ProxyServer(
        id=FAKE_ID,
        ip_address=proxy_server.ip_address + '2',
        name=proxy_server.name + '2',
        ssh_private_key=proxy_server.ssh_private_key + '2',
        fingerprint=proxy_server.fingerprint + '2')

    form_data = {
      'ip_address': updated_proxy_server.ip_address,
      'name': updated_proxy_server.name,
      'ssh_private_key': updated_proxy_server.ssh_private_key,
      'fingerprint': updated_proxy_server.fingerprint
    }

    resp = self.client.post(
        flask.url_for('proxyserver_edit', server_id=FAKE_ID), 
        data=form_data)

    updated_proxy_server_in_db = models.ProxyServer.query.get(FAKE_ID)
    self.assertEqual(updated_proxy_server.name,
                     updated_proxy_server_in_db.name)
    self.assertEqual(updated_proxy_server.ip_address,
                     updated_proxy_server_in_db.ip_address)
    self.assertEqual(updated_proxy_server.ssh_private_key,
                     updated_proxy_server_in_db.ssh_private_key)
    self.assertEqual(updated_proxy_server.fingerprint,
                     updated_proxy_server_in_db.fingerprint)

    self.assert_redirects(resp, flask.url_for('proxyserver_list'))

  def testDeleteProxyServerPostHandler(self):
    proxy_server = self._CreateAndSaveFakeProxyServer()

    self.assertIsNotNone(models.ProxyServer.query.get(FAKE_ID))

    response = self.client.get(flask.url_for('proxyserver_delete',
                                server_id=FAKE_ID),
                                follow_redirects=False)

    self.assertIsNone(models.ProxyServer.query.get(FAKE_ID))
    self.assert_redirects(response, flask.url_for('proxyserver_list'))

  def _CreateAndSaveFakeProxyServer(self):
    """Create a fake proxy server, and save it into db."""
    proxy_server = models.ProxyServer(
        id=FAKE_ID,
        ip_address=FAKE_PROXY_SERVER_DATA[0]['ip_address'],
        name=FAKE_PROXY_SERVER_DATA[0]['name'],
        ssh_private_key=FAKE_PROXY_SERVER_DATA[0]['ip_address'],
        fingerprint=FAKE_PROXY_SERVER_DATA[0]['fingerprint'])
    proxy_server.save()
    return proxy_server

if __name__ == '__main__':
  unittest.main()
