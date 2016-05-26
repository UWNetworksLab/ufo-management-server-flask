"""Configurations for running in production and testing.

More info about this structure can be found here:
https://realpython.com/blog/python/python-web-applications-with-flask-part-iii/
"""
import os

from ufo import app


class BaseConfiguration(object):
  """Configurations for running the application in production."""

  TESTING = False
  SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  SECRET_KEY = 'NOT VERY SECRET'

  SHARED_OAUTH_CLIENT_ID = '84596478403-6uffc6hu8v5b6v3nh0ski5cbptl02dsd.apps.googleusercontent.com'
  SHARED_OAUTH_CLIENT_SECRET = 'R5H27t1C-9enMO9ZNfxym3Gw'
  WHOOSH_BASE = 'sqlite:///' + os.path.join(app.instance_path, 'search.db')
  RECAPTCHA_SITE_KEY = '6LcGsiATAAAAAMzn-dtA9_73dPktkof7bDUIZxtK'

class TestConfiguration(BaseConfiguration):
  """Configurations for testing the application in development."""

  TESTING = True

  SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
  # Unit tests are normally run in memory for speed, but a test db
  # configuration is below if necessary.
  # 'sqlite:///' + os.path.join(app.instance_path, 'test.db')

  # Since we want our unit tests to run quickly we turn this down - the
  # hashing is still done but the time-consuming part is left out.
  HASH_ROUNDS = 1
