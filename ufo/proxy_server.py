"""The module for handling proxy servers"""

from . import app, db, setup_required

import flask
import models
import ssh_client
import StringIO


def _GetViewDataFromProxyServer(server):
  public_key = ssh_client.SSHClient.public_key_data_to_object(
      server.host_public_key_type,
      server.host_public_key)
  private_key = ssh_client.SSHClient.private_key_data_to_object(
      server.ssh_private_key_type,
      server.ssh_private_key)
  private_key_file = StringIO.StringIO()
  private_key.write_private_key(private_key_file)
  private_key_text = private_key_file.getvalue()

  return {
    "id": server.id,
    "name": server.name,
    "ip_address": server.ip_address,
    "public_key": public_key.get_name() + ' ' + public_key.get_base64(),
    "private_key": private_key_text,
    }


@app.route('/proxyserver/')
@setup_required
def proxyserver_list():
  proxy_servers_data = models.ProxyServer.query.all()
  proxy_servers = [_GetViewDataFromProxyServer(s) for s in proxy_servers_data]

  return flask.render_template('proxy_server.html',
                               proxy_servers=proxy_servers)

@app.route('/proxyserver/add', methods=['GET', 'POST'])
@setup_required
def proxyserver_add():
  """Get the form for adding new proxy servers."""
  if flask.request.method == 'GET':
    return flask.render_template('proxy_server_form.html',
                                 proxy_server=None)

  server = models.ProxyServer(
      name=flask.request.form.get('name'),
      ip_address=flask.request.form.get('ip_address'))

  #TODO more robust validation here and in proxyserver_edit
  public_key_contents = flask.request.form.get('public_key')
  if public_key_contents is None:
    flask.abort(400)

  private_key_contents = flask.request.form.get('private_key')
  if private_key_contents is None:
    flask.abort(400)

  server.read_public_key_from_file_contents(public_key_contents)
  server.read_private_key_from_file_contents(private_key_contents)

  server.save()

  return flask.redirect(flask.url_for('proxyserver_list'))

@app.route('/proxyserver/<server_id>/edit', methods=['GET', 'POST'])
@setup_required
def proxyserver_edit(server_id):
  server = models.ProxyServer.query.get_or_404(server_id)

  if flask.request.method == 'GET':
    server_for_view = _GetViewDataFromProxyServer(server)
    return flask.render_template('proxy_server_form.html',
                                 proxy_server=server_for_view)

  server.name = flask.request.form.get('name')
  server.ip_address = flask.request.form.get('ip_address')

  server.read_public_key_from_file_contents(flask.request.form.get('public_key'))
  server.read_private_key_from_file_contents(flask.request.form.get('private_key'))
  server.save()

  return flask.redirect(flask.url_for('proxyserver_list'))

@app.route('/proxyserver/<server_id>/delete')
@setup_required
def proxyserver_delete(server_id):
  """Handler for deleting an existing proxy server."""
  #TODO should at least be post
  server = models.ProxyServer.query.get_or_404(server_id)
  server.delete()

  return flask.redirect(flask.url_for('proxyserver_list'))
