"""The module for handling proxy servers"""
import json

import flask

import ufo
from ufo.database import models
from ufo.services import regex
from ufo.services import ssh_client


def get_proxy_resources_dict():
  """Get the resources for the proxy server component.

    Returns:
      A dict of the resources for the proxy server component.
  """
  return {
    'addUrl': flask.url_for('proxyserver_add'),
    'addIconUrl': flask.url_for('static', filename='img/add-servers.svg'),
    'inverseAddIconUrl': flask.url_for('static', filename='img/add-servers-inverse.svg'),
    'addText': 'Add a Server',
    'listId': 'proxyList',
    'listUrl': flask.url_for('proxyserver_list'),
    'listLimit': 10,
    'detailsButtonText': 'Edit Server',
    'detailsButtonId': 'serverEditButton',
    'detailsOverlayId': 'serverEditOverlay',
    'seeAllText': 'See All Servers',
    'titleText': 'Servers',
    'itemIconUrl': flask.url_for('static', filename='img/server.svg'),
    'isProxyServer': True,
    'hasAddFlow': True,
    'modalId': 'serverModal',
    'dismissText': 'Cancel',
    'confirmText': 'Add Server',
    'regexes': regex.REGEXES_AND_ERRORS_DICTIONARY,
    'textAreaMaxRows': 10,
    'ipLabel': 'IP Address',
    'nameLabel': 'Server Name',
    'privateKeyLabel': 'SSH Private Key',
    'publicKeyLabel': 'SSH Host Public Key',
    'ip_address': '',
    'name': '',
    'private_key': '',
    'public_key': '',
    'privateKeyText': ('For the private key, please copy the full contents of '
                       'a private key file with the ability to access a proxy '
                       'server. The beginning of the file should resemble '
                       '"-----BEGIN RSA PRIVATE KEY-----".'),
    'publicKeyText': ('For the hosts public key, you can usually get this '
                      'value from either /etc/ssh/ssh_host_rsa_key.pub or from'
                      ' the line in $HOME/.ssh/known_hosts on your server.'),
    'rsaText': ('For now, please be sure to use an RSA key (the text should '
                'begin with ssh-rsa)'),
  }

@ufo.app.route('/proxyserver/')
@ufo.setup_required
def proxyserver_list():
  proxy_server_dict = {'items': models.ProxyServer.get_items_as_list_of_dict()}
  proxy_servers_json = json.dumps((proxy_server_dict))
  return flask.Response(proxy_servers_json, mimetype='application/json')

@ufo.app.route('/proxyserver/add', methods=['GET', 'POST'])
@ufo.setup_required
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

@ufo.app.route('/proxyserver/<server_id>/edit', methods=['GET', 'POST'])
@ufo.setup_required
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

@ufo.app.route('/proxyserver/<server_id>/delete')
@ufo.setup_required
def proxyserver_delete(server_id):
  """Handler for deleting an existing proxy server."""
  #TODO should at least be post
  server = models.ProxyServer.query.get_or_404(server_id)
  server.delete()

  return flask.redirect(flask.url_for('proxyserver_list'))
