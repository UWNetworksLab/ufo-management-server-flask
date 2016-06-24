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

# There's an issue in the web driver tests with our vulcanized JS and HTML
# files getting cached and executing the i18n calls early, such as before the
# messages.json file is loaded. Making the files not cached fixes this for now.
# TODO(eholder): Investigate other solutions instead of not caching the
# vulcanized files.
@ufo.app.route('/vulcanized_html')
def vulcanized_html():
  return flask.send_file('static/vulcanized.html', cache_timeout=1)

@ufo.app.route('/vulcanized_js')
def vulcanized_js():
  return flask.send_file('static/vulcanized.js', cache_timeout=1)


# The following imports are commented out since they are already
# imported above, but are kept here for posterity.
from ufo.handlers import admin
#from ufo.handlers import chrome_policy
#from ufo.handlers import proxy_server
from ufo.handlers import setup
from ufo.handlers import search
from ufo.handlers import settings
#from ufo.handlers import user
