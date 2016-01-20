"""Base test with common setup and teardown."""

from flask.ext.testing import TestCase

from . import app
from . import db
import models


class BaseTest(TestCase):
  """Base test with comment setup and teardown."""

  def create_app(self):
    app.config.from_object('config.TestConfiguration')
    return app

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    db.create_all()

  def setup_config(self):
    """Setup the config that is needed for @setup_required decorator."""
    self.config = models.Config()
    self.config.isConfigured = True
    self.config.id = 0

    self.config.Add()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
