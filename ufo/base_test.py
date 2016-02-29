"""Base test with common setup and teardown."""

from flask.ext.testing import TestCase

import ufo
from ufo.database import models


class BaseTest(TestCase):
  """Base test with comment setup and teardown."""

  def create_app(self):
    ufo.app.config.from_object('config.TestConfiguration')
    return ufo.app

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    ufo.db.create_all()

  def setup_config(self):
    """Setup the config that is needed for @setup_required decorator."""
    self.config = models.Config()
    self.config.isConfigured = True
    self.config.id = 0

    self.config.save()

  def tearDown(self):
    ufo.db.session.remove()
    ufo.db.drop_all()
