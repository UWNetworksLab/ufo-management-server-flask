"""The module for handling proxy servers"""

from . import app, db, setup_required

import flask
import json

import ufo
from ufo import models
from ufo import ssh_client


def get_proxy_resources_dict():
  """Get the resources for the proxy server component.

    Returns:
      A dict of the resources for the proxy server component.
  """
  return {
    'addUrl': flask.url_for('proxyserver_add'),
    'addIconUrl': flask.url_for('static', filename='img/add-servers.svg'),
    'addText': 'Add a Server',
    'listId': 'proxyList',
    'listUrl': flask.url_for('proxyserver_list'),
    'listLimit': 10,
    'seeAllText': 'See All Servers',
    'titleText': 'Servers',
    'itemIconUrl': flask.url_for('static', filename='img/server.svg'),
    'isProxyServer': True,
    'modalId': 'serverModal',
    'dismissText': 'Cancel',
    'confirmText': 'Add Server',
  }

@app.route('/proxyserver/')
@setup_required
def proxyserver_list():
  proxy_server_dict = {'items': models.ProxyServer.get_items_as_list_of_dict()}
  proxy_servers_json = json.dumps((proxy_server_dict))
  return flask.Response(proxy_servers_json, mimetype='application/json')

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
    server_for_view = server.to_dict()
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
