"""The module for handling proxy servers"""

from . import app, db, setup_required

import logging
import flask
import models


def _MakeKeyString():
  """Generate the key string in open ssh format for pushing to proxy servers.

  This key string includes only the public key for each user in order to grant
  the user access to each proxy server.

  Returns:
    key_string: A string of users with associated key.
  """
  users = models.User.query.all()
  key_string = ''
  ssh_starting_portion = 'ssh-rsa'
  space = ' '
  endline = '\n'
  for user in users:
    if not user.is_key_revoked:
      user_string = (ssh_starting_portion + space + user.public_key + space +
                     user.email + endline)
      key_string += user_string

  return key_string

def _SendKeysToServer(server, keys):
  #TODO implement
  pass

@app.route('/proxyserver/list')
@setup_required
def proxyserver_list():
  proxy_servers = models.ProxyServer.query.all()
  print proxy_servers
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
      ip_address=flask.request.form.get('ip_address'),
      ssh_private_key=flask.request.form.get('ssh_private_key'),
      fingerprint=flask.request.form.get('fingerprint'))
  db.session.add(server)

  return flask.redirect(flask.url_for('proxyserver_list'))

@app.route('/proxyserver/<server_id>/edit', methods=['GET', 'POST'])
@setup_required
def proxyserver_edit(server_id):
  server = models.ProxyServer.query.get_or_404(server_id)

  if flask.request.method == 'GET':
    return flask.render_template('proxy_server_form.html',
                                 proxy_server=server)

  server.name = flask.request.form.get('name')
  server.ip_address = flask.request.form.get('ip_address')
  server.ssh_private_key = flask.request.form.get('ssh_private_key')
  server.fingerprint = flask.request.form.get('fingerprint')

  return flask.redirect(flask.url_for('proxyserver_list'))

@app.route('/proxyserver/<server_id>/delete')
@setup_required
def proxyserver_delete(server_id):
  """Handler for deleting an existing proxy server."""
  #TODO should at least be post
  server = models.ProxyServer.query.get_or_404(server_id)

  db.session.delete(server)

  return flask.redirect(flask.url_for('proxyserver_list'))

#TODO use task queues, split this up a bit
@app.route('/cron/proxyserver/distributekeys')
@setup_required
def proxyserver_distributekeys():
  key_string = _MakeKeyString()
  proxy_servers = models.ProxyServer.query.all()
  for proxy_server in proxy_servers:
    _SendKeysToServer(proxy_server, key_string)
  return 'Done!'
