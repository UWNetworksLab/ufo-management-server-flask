import flask
import json

from ufo import app
from ufo import component_resources
from ufo import get_user_config


@app.route('/')
def landing():
  config = get_user_config()
  return flask.render_template('landing.html',
                               site_verification_content=config.dv_content)

@app.route('/new')
def new_landing():
  user_resources_dict = component_resources._get_user_resources_dict()
  proxy_resources_dict = component_resources._get_proxy_resources_dict()
  policy_resources_dict = component_resources._get_policy_resources_dict()

  return flask.render_template(
      'landing2.html',
      user_resources=json.dumps(user_resources_dict),
      proxy_resources=json.dumps(proxy_resources_dict),
      policy_resources=json.dumps(policy_resources_dict))


from ufo import setup # handlers for /setup
from ufo import user # handlers for /user
from ufo import proxy_server # handlers for /proxy_server
from ufo import chrome_policy # handlers for /chrome_policy
