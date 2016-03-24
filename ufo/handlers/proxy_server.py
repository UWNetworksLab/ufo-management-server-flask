"""The module for handling proxy servers"""
import json

import flask

import ufo
from ufo.database import models
from ufo.handlers import auth
from ufo.services import regex
from ufo.services import ssh_client
from ufo.services import custom_exceptions


@ufo.app.route('/proxyserver/')
@ufo.setup_required
@auth.login_required
def proxyserver_list():
  proxy_server_dict = {'items': models.ProxyServer.get_items_as_list_of_dict()}
  proxy_servers_json = json.dumps((proxy_server_dict))
  return flask.Response(proxy_servers_json, mimetype='application/json')

@ufo.app.route('/proxyserver/add', methods=['GET', 'POST'])
@ufo.setup_required
@auth.login_required
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

  try:
    server.save()
  except custom_exceptions.UnableToSaveToDB as e:
    flask.abort(e.code, e.message)

  return flask.redirect(flask.url_for('proxyserver_list'))

@ufo.app.route('/proxyserver/edit', methods=['POST'])
@ufo.setup_required
@auth.login_required
def proxyserver_edit():

  server_id = json.loads(flask.request.form.get('server_id'))
  server = models.ProxyServer.query.get_or_404(server_id)
  server.name = flask.request.form.get('name')
  server.ip_address = flask.request.form.get('ip_address')

  server.read_public_key_from_file_contents(flask.request.form.get('public_key'))
  server.read_private_key_from_file_contents(flask.request.form.get('private_key'))
  server.save()

  return flask.redirect(flask.url_for('proxyserver_list'))

@ufo.app.route('/proxyserver/delete', methods=['POST'])
@ufo.setup_required
@auth.login_required
def proxyserver_delete():
  """Handler for deleting an existing proxy server."""
  server_id = json.loads(flask.request.form.get('server_id'))
  server = models.ProxyServer.query.get_or_404(server_id)
  server.delete()

  return flask.redirect(flask.url_for('proxyserver_list'))
