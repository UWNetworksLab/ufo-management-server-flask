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
    'addIconUrl': flask.url_for('static', filename='img/add-users.svg'),
    'addText': 'Add Users',
    'listUrl': flask.url_for('user_list'),
    'listLimit': 10,
    'seeAllText': 'See All Users',
    'titleText': 'Users',
    'itemIconUrl': flask.url_for('static', filename='img/user.svg'),
    'isUser': True,
    'modalId': 'userModal',
    'dismissText': 'Cancel',
    'addFlowTextDicts': [
        {
          'tab': 'Add Group',
          'saveButton': 'Add Group',
          'searchButton': 'Search for Users in Group',
          'label1': ('Input a group key (group email address or unique id) '
                     'to fetch more users.'),
        },
        {
          'tab': 'Add Individual',
          'saveButton': 'Add User',
          'searchButton': 'Search for Specific User',
          'label1': ('Input user key (email address or unique id) to search '
                     'for a specific user.'),
        },
        {
          'tab': 'Add by Domain',
          'saveButton': 'Add Users',
          'searchButton': 'Search for Users in Domain',
        },
        {
          'tab': 'Add Manually',
          'saveButton': 'Add User',
          'label1': 'Input user name here.',
          'label2': 'Input user email here.',
        },
    ],
  }
  proxy_resources_dict = {
    'addUrl': flask.url_for('proxyserver_add'),
    'addIconUrl': flask.url_for('static', filename='img/add-servers.svg'),
    'addText': 'Add a Server',
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
  policy_resources_dict = {
    'titleText': 'Chrome Policy',
    'isChromePolicy': True,
  }
  return flask.render_template(
      'landing2.html',
      user_resources=json.dumps((user_resources_dict)),
      proxy_resources=json.dumps((proxy_resources_dict)),
      policy_resources=json.dumps((policy_resources_dict)))

import setup # handlers for /setup
import user # handlers for /user
import proxy_server # handlers for /proxy_server
import chrome_policy # handlers for /chrome_policy
