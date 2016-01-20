"""Test setup module functionality."""
from mock import MagicMock
from mock import patch

import flask
from googleapiclient import discovery
import unittest

from . import app
import base_test
from . import db
import models
import oauth
import setup

FAKE_OAUTH_URL = 'sftp://1800-oauth.com'

class SetupTest(base_test.BaseTest):
  """Test setup class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(SetupTest, self).setUp()
    super(SetupTest, self).setup_config()

  @patch('flask.render_template')
  def testNotSetupHandler(self, mock_render_template):
    """Test the not setup handler loads the error page as called."""
    mock_render_template.return_value = ''

    resp = self.client.get(flask.url_for('not_setup'))

    args, kwargs = mock_render_template.call_args
    self.assertEquals('error.html', args[0])
    self.assertEquals(setup.PLEASE_CONFIGURE_TEXT, kwargs['error_text'])

  @patch.object(oauth, 'getOauthFlow')
  @patch('flask.render_template')
  def testGetSetupHandler(self, mock_render_template, mock_oauth_flow):
    """Test get on the setup handler loads the setup page."""
    mock_render_template.return_value = ''
    flow_object = mock_oauth_flow.return_value
    flow_object.step1_get_authorize_url.return_value = FAKE_OAUTH_URL

    resp = self.client.get(flask.url_for('setup'))

    args, kwargs = mock_render_template.call_args
    self.assertEquals('setup.html', args[0])
    self.assertEquals(self.config, kwargs['config'])
    self.assertEquals(FAKE_OAUTH_URL, kwargs['oauth_url'])

  @patch.object(discovery, 'build')
  @patch.object(oauth, 'getOauthFlow')
  @patch('flask.render_template')
  def testPostSetupIncorrectDomain(self, mock_render_template,
                                   mock_oauth_flow, mock_build):
    """Test posting to setup with an incorrect domain generates an error."""
    mock_render_template.return_value = ''
    flow_object = mock_oauth_flow.return_value
    flow_object.step1_get_authorize_url.return_value = FAKE_OAUTH_URL
    fake_domain = 'yahoo.com'
    domain_that_doesnt_match = 'google.com'
    fake_oauth_code = 'foobar'
    # This weird looking structure is to mock out a call buried behind several
    # objects which requires going through the method's return_value for each
    # method down the chain, starting from the discovery module.
    build_object = mock_build.return_value
    people_object = build_object.people.return_value
    get_object = people_object.get.return_value
    get_object.execute.return_value = {'domain': domain_that_doesnt_match}

    form_data = {}
    form_data['oauth_code'] = fake_oauth_code
    form_data['domain'] = fake_domain

    resp = self.client.post(flask.url_for('setup'), data=form_data)

    args, kwargs = mock_render_template.call_args
    self.assertEquals('setup.html', args[0])
    self.assertEquals(setup.DOMAIN_INVALID_TEXT, kwargs['error'])
    self.assertEquals(self.config, kwargs['config'])
    self.assertEquals(FAKE_OAUTH_URL, kwargs['oauth_url'])


if __name__ == '__main__':
  unittest.main()
