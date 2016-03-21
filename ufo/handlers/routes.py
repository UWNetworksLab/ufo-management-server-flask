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

  return flask.render_template('landing.html')


# The following imports are commented out since they are already
# imported above, but are kept here for posterity.
#from ufo.handlers import chrome_policy
#from ufo.handlers import proxy_server
from ufo.handlers import setup
from ufo.handlers import search
from ufo.handlers import settings
#from ufo.handlers import user
