import binascii
import os

import flask

import ufo


@ufo.app.before_request
def xsrf_protect():
  """Verifies that an xsrf token is included for all non-get requests

  Slight modification of http://flask.pocoo.org/snippets/3/
  """
  if ufo.app.config['TESTING']:
    return
  if flask.request.method != 'GET':
    token = flask.session.pop('_xsrf_token', None)
    if not token or token != flask.request.form.get('_xsrf_token'):
      flask.abort(403)

def generate_xsrf_token():
  if '_xsrf_token' not in flask.session:
    flask.session['_xsrf_token'] = binascii.b2a_hex(os.urandom(16))
  return flask.session['_xsrf_token']

ufo.app.jinja_env.globals['xsrf_token'] = generate_xsrf_token
