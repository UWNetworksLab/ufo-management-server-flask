import json

import flask

import ufo
from ufo.handlers import auth
from ufo.handlers import chrome_policy
from ufo.handlers import proxy_server
from ufo.handlers import user


@ufo.app.route('/')
@ufo.setup_required
@auth.login_required
def landing():
  user_resources_dict = user.get_user_resources_dict()
  proxy_resources_dict = proxy_server.get_proxy_resources_dict()
  policy_resources_dict = chrome_policy.get_policy_resources_dict()

  return flask.render_template(
      'landing.html',
      user_resources=json.dumps(user_resources_dict),
      proxy_server_resources=json.dumps(proxy_resources_dict),
      policy_resources=json.dumps(policy_resources_dict))


# The following imports are commented out since they are already
# imported above, but are kept here for posterity.
#from ufo.handlers import chrome_policy
#from ufo.handlers import proxy_server
from ufo.handlers import setup
from ufo.handlers import search
from ufo.handlers import settings
#from ufo.handlers import user
