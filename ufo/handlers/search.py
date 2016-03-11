"""Search module which provides handlers to locate users and proxy servers."""

import json

import flask
# Renaming search to sa_search to avoid name conflicts.
from sqlalchemy_searchable import search as sa_search

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
  user_resources_dict = user.get_user_resources_dict()
  user_resources_dict['hasAddFlow'] = False
  user_results = models.User.search(search_text)
  user_items = json.dumps(({'items': user_results}))
  proxy_server_resources_dict = proxy_server.get_proxy_resources_dict()
  proxy_server_resources_dict['hasAddFlow'] = False
  proxy_server_results = models.ProxyServer.search(search_text)
  proxy_server_items = json.dumps(({'items': proxy_server_results}))

  return flask.render_template(
      'search.html',
      user_resources=json.dumps(user_resources_dict),
      user_items=user_items,
      proxy_server_resources=json.dumps(proxy_server_resources_dict),
      proxy_server_items=proxy_server_items)
