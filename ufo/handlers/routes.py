import json

import flask

import ufo
from ufo.handlers import chrome_policy
from ufo.handlers import proxy_server
from ufo.handlers import user


@ufo.app.route('/')
def landing():
  config = ufo.get_user_config()
  return flask.render_template('landing.html',
                               site_verification_content=config.dv_content)

@ufo.app.route('/new')
def new_landing():
  user_resources_dict = user.get_user_resources_dict()
  proxy_resources_dict = proxy_server.get_proxy_resources_dict()
  policy_resources_dict = chrome_policy.get_policy_resources_dict()

  return flask.render_template(
      'landing2.html',
      user_resources=json.dumps(user_resources_dict),
      proxy_resources=json.dumps(proxy_resources_dict),
      policy_resources=json.dumps(policy_resources_dict))


from ufo.handlers import chrome_policy
from ufo.handlers import proxy_server
from ufo.handlers import setup
from ufo.handlers import search
from ufo.handlers import user
