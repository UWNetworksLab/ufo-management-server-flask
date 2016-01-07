from . import app, get_user_config

import flask

@app.route('/')
def landing():
  config = get_user_config()
  return flask.render_template('landing.html',
                               site_verification_content=config.dv_content)

import setup # handlers for /setup
import user # handlers for /user
import proxy_server # handlers for /proxy_server
