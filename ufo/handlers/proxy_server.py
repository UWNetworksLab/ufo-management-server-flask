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
  return flask.Response(ufo.XSSI_PREFIX + proxy_servers_json,
                        headers=ufo.JSON_HEADERS)

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
  host_public_key_contents = flask.request.form.get('host_public_key')
  if host_public_key_contents is None:
    flask.abort(400)

  ssh_private_key_contents = flask.request.form.get('ssh_private_key')
  if ssh_private_key_contents is None:
    flask.abort(400)

  server.read_public_key_from_file_contents(host_public_key_contents)
  server.read_private_key_from_file_contents(ssh_private_key_contents)

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

  host_public_key_contents = flask.request.form.get('host_public_key')
  ssh_private_key_contents = flask.request.form.get('ssh_private_key')
  if ssh_private_key_contents.find('\n') == -1:
    ssh_private_key_contents = (
        _fix_new_line_key_format(ssh_private_key_contents))
  server.read_public_key_from_file_contents(host_public_key_contents)
  server.read_private_key_from_file_contents(ssh_private_key_contents)
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

def _fix_new_line_key_format(private_key_string):
  """Format a private key string with new lines.

  Args:
    private_key_string: A private key as a string without newlines.

  Returns:
    The same private key string with new lines inserted as necessary. If the
    format of the input string is not as expected, the original string is
    returned, unaltered instead.
  """
  newline = '\n'
  private_key_dash = ' PRIVATE KEY-----'
  end_key_dash = '-----END'
  every = 64
  beginning_index = private_key_string.find(private_key_dash)
  ending_index = private_key_string.find(end_key_dash)
  if beginning_index == -1 or ending_index == -1:
    # The format was not as expected, so just return the default string.
    return private_key_string

  total_beginning_index = beginning_index + len(private_key_dash)
  beginning_portion = private_key_string[0:total_beginning_index]
  ending_portion = private_key_string[ending_index:]
  actual_key = private_key_string[total_beginning_index:ending_index]

  lines = [beginning_portion]
  for i in range(0, len(actual_key), every):
    lines.append(actual_key[i:i+every])
  lines.append(ending_portion)
  return newline.join(lines)
