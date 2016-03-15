"""Search module which provides handlers to locate users and proxy servers."""

import json

import flask

import ufo
from ufo.database import models
from ufo.handlers import user
from ufo.handlers import proxy_server


@ufo.app.route('/search/', methods=['GET'])
@ufo.setup_required
def search_page():
  """Renders the basic search page template.

  Returns:
    A rendered template of search.html.
  """
  search_text = json.loads(flask.request.args.get('search_text'))
  user_items = _user_search_json_helper(search_text)
  proxy_server_items = _server_search_json_helper(search_text)

  user_resources_dict = user.get_user_resources_dict()
  user_resources_dict['hasAddFlow'] = False
  proxy_server_resources_dict = proxy_server.get_proxy_resources_dict()
  proxy_server_resources_dict['hasAddFlow'] = False

  return flask.render_template(
      'search.html',
      user_resources=json.dumps(user_resources_dict),
      proxy_server_resources=json.dumps(proxy_server_resources_dict),
      user_items=json.dumps(user_items),
      proxy_server_items=json.dumps(proxy_server_items))

@ufo.app.route('/search_results/', methods=['GET'])
@ufo.setup_required
def search_json():
  """Gets the database entities matching the search term.

  Returns:
    A flask response json object with users set to the users found and servers
    set to the proxy servers found.
  """
  search_text = json.loads(flask.request.args.get('search_text'))
  results_json = _search_json_helper(search_text)
  return flask.Response(results_json, mimetype='application/json')

def _search_json_helper(search_text):
  """Gets the database entities matching the search term.

  Args:
    search_text: A string for the search term.

  Returns:
    A json object with users set to the users found and servers set to the
    proxy servers found.
  """
  results_dict = {
    'users': _user_search_json_helper(search_text),
    'servers': _server_search_json_helper(search_text),
  }
  return json.dumps((results_dict))

def _user_search_json_helper(search_text):
  """Gets the database users matching the search term.

  Args:
    search_text: A string for the search term.

  Returns:
    A dict object with items set to the users found.
  """
  results_dict = {
    'items': models.User.search(search_text),
  }
  return results_dict

def _server_search_json_helper(search_text):
  """Gets the database proxy servers matching the search term.

  Args:
    search_text: A string for the search term.

  Returns:
    A dict object with items set to the proxy servers found.
  """
  results_dict = {
    'items': models.ProxyServer.search(search_text),
  }
  return results_dict
