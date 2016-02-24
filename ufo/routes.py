from . import app, get_user_config

import flask
import json

@app.route('/')
def landing():
  config = get_user_config()
  return flask.render_template('landing.html',
                               site_verification_content=config.dv_content)

@app.route('/new')
def new_landing():
  user_resources_dict = {
    'addUrl': flask.url_for('add_user'),
    'addIconUrl': flask.url_for('static', filename='add-users.svg'),
    'addText': 'Add Users',
    'listUrl': flask.url_for('user_list'),
    'titleText': 'Users',
    'itemIconUrl': flask.url_for('static', filename='user.svg'),
    'isUser': True,
    'isProxyServer': False,
  }
  proxy_resources_dict = {
    'addUrl': flask.url_for('proxyserver_add'),
    'addIconUrl': flask.url_for('static', filename='add-servers.svg'),
    'addText': 'Add a Server',
    'listUrl': flask.url_for('proxyserver_list'),
    'titleText': 'Servers',
    'itemIconUrl': flask.url_for('static', filename='server.svg'),
    'isUser': False,
    'isProxyServer': True,
  }
  return flask.render_template(
  	  'landing2.html',
  	  user_resources=json.dumps((user_resources_dict)),
  	  proxy_resources=json.dumps((proxy_resources_dict)))

import setup # handlers for /setup
import user # handlers for /user
import proxy_server # handlers for /proxy_server
import chrome_policy # handlers for /chrome_policy
