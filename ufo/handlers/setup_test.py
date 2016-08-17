"""Test setup module functionality."""
import json
import unittest

import flask
from googleapiclient import discovery
from mock import MagicMock
from mock import patch

import ufo
from ufo import base_test
from ufo.database import models
from ufo.handlers import setup
from ufo.services import oauth


FAKE_OAUTH_URL = 'sftp://1800-oauth.com'
FAKE_DOMAIN = 'yahoo.com'
FAKE_OAUTH_CODE = 'foobar'
FAKE_CREDENTIALS = 'I am some fake credentials.'
FAKE_ADMIN_EMAIL = 'some_fake_email@admin.com'
FAKE_ADMIN_PASSWORD = 'some fake password'
MOCK_CREDENTIALS = MagicMock()
MOCK_CREDENTIALS.authorize.return_value = None
MOCK_CREDENTIALS.to_json.return_value = FAKE_CREDENTIALS
MOCK_CREDENTIALS.__str__.return_value = FAKE_CREDENTIALS


class SetupTest(base_test.BaseTest):
  """Test setup class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(SetupTest, self).setUp()
    super(SetupTest, self).setup_auth();

  @patch('flask.render_template')
  def testGetSetupHandler(self, mock_render_template):
    """Test get on the setup handler loads the setup page."""
    mock_render_template.return_value = ''

    resp = self.client.get(flask.url_for('setup'))

    args, kwargs = mock_render_template.call_args
    self.assertEquals('setup.html', args[0])
    self.assertIsNotNone(kwargs['configuration_resources'])
    self.assertIsNotNone(kwargs['oauth_url'])

  @patch.object(discovery, 'build')
  @patch.object(oauth, 'getOauthFlow')
  def testPostOauthSetupIncorrectDomain(self, mock_oauth_flow, mock_build):
    """Test posting to setup with an incorrect domain generates an error."""
    domain_that_doesnt_match = 'google.com'
    # This weird looking structure is to mock out a call buried behind several
    # objects which requires going through the method's return_value for each
    # method down the chain, starting from the discovery module.
    build_object = mock_build.return_value
    people_object = build_object.people.return_value
    get_object = people_object.get.return_value
    get_object.execute.return_value = {'domain': domain_that_doesnt_match}
    returned_mock = mock_oauth_flow.return_value
    returned_mock.step2_exchange.return_value = MOCK_CREDENTIALS
    returned_mock.step1_get_authorize_url.return_value = FAKE_OAUTH_URL

    form_data = {}
    form_data['oauth_code'] = FAKE_OAUTH_CODE
    form_data['domain'] = FAKE_DOMAIN

    resp = self.client.post(flask.url_for('setup_oauth'), data=form_data)

    json_response = json.loads(resp.data[len(ufo.XSSI_PREFIX):])
    self.assertEquals(403, json_response['code'])
    self.assertEquals(setup.DOMAIN_INVALID_TEXT, json_response['message'])

  @patch.object(discovery, 'build')
  @patch.object(oauth, 'getOauthFlow')
  def testPostOauthSetupNonDomainAdmin(self, mock_oauth_flow, mock_build):
    """Test posting to setup as a non-admin domain user generates an error."""
    fake_id = 'user@foocompany.com'
    # This weird looking structure is to mock out a call buried behind several
    # objects which requires going through the method's return_value for each
    # method down the chain, starting from the discovery module.
    build_object = mock_build.return_value
    people_object = build_object.people.return_value
    get_object = people_object.get.return_value
    get_object.execute.return_value = {'domain': FAKE_DOMAIN, 'id': fake_id}
    users_object = build_object.users.return_value
    users_object.get.return_value.execute.return_value = {'isAdmin': False}
    returned_mock = mock_oauth_flow.return_value
    returned_mock.step2_exchange.return_value = MOCK_CREDENTIALS
    returned_mock.step1_get_authorize_url.return_value = FAKE_OAUTH_URL

    form_data = {}
    form_data['oauth_code'] = FAKE_OAUTH_CODE
    form_data['domain'] = FAKE_DOMAIN

    resp = self.client.post(flask.url_for('setup_oauth'), data=form_data)

    json_response = json.loads(resp.data[len(ufo.XSSI_PREFIX):])
    self.assertEquals(403, json_response['code'])
    self.assertEquals(setup.NON_ADMIN_TEXT, json_response['message'])

  @patch.object(oauth, 'getOauthFlow')
  @patch.object(discovery, 'build')
  def testPostOauthSetup(self, mock_build, mock_oauth_flow):
    """Test posting to setup with correct values goes through."""
    fake_id = 'user@foocompany.com'
    # This weird looking structure is to mock out a call buried behind several
    # objects which requires going through the method's return_value for each
    # method down the chain, starting from the discovery module.
    build_object = mock_build.return_value
    people_object = build_object.people.return_value
    get_object = people_object.get.return_value
    get_object.execute.return_value = {'domain': FAKE_DOMAIN, 'id': fake_id}
    users_object = build_object.users.return_value
    users_object.get.return_value.execute.return_value = {'isAdmin': True}
    returned_mock = mock_oauth_flow.return_value
    returned_mock.step2_exchange.return_value = MOCK_CREDENTIALS
    returned_mock.step1_get_authorize_url.return_value = FAKE_OAUTH_URL

    config = models.Config.query.get(0)
    self.assertIsNone(config)

    form_data = {}
    form_data['oauth_code'] = FAKE_OAUTH_CODE
    form_data['domain'] = FAKE_DOMAIN

    resp = self.client.post(flask.url_for('setup_oauth'), data=form_data)

    config = models.Config.query.get(0)
    self.assertIsNotNone(config)
    self.assertEquals(config.credentials, FAKE_CREDENTIALS)
    self.assertEquals(config.domain, FAKE_DOMAIN)

    json_response = json.loads(resp.data[len(ufo.XSSI_PREFIX):])
    self.assertEquals(FAKE_DOMAIN, json_response['domain'])
    self.assertEquals(FAKE_CREDENTIALS, json_response['credentials'])

  def testPostAdminSetupNonAdmin(self):
    """Test posting to admin setup without specifying an admin throws error."""
    form_data = {}

    resp = self.client.post(flask.url_for('setup_admin'), data=form_data)

    json_response = json.loads(resp.data[len(ufo.XSSI_PREFIX):])
    self.assertEquals(403, json_response['code'])
    self.assertEquals(setup.NO_ADMINISTRATOR, json_response['message'])

    form_data = {}
    form_data['admin_email'] = FAKE_ADMIN_EMAIL

    resp = self.client.post(flask.url_for('setup_admin'), data=form_data)

    json_response = json.loads(resp.data[len(ufo.XSSI_PREFIX):])
    self.assertEquals(403, json_response['code'])
    self.assertEquals(setup.NO_ADMINISTRATOR, json_response['message'])

    form_data = {}
    form_data['admin_password'] = FAKE_ADMIN_PASSWORD

    resp = self.client.post(flask.url_for('setup_admin'), data=form_data)

    json_response = json.loads(resp.data[len(ufo.XSSI_PREFIX):])
    self.assertEquals(403, json_response['code'])
    self.assertEquals(setup.NO_ADMINISTRATOR, json_response['message'])

  def testPostAdminSetupAlreadySet(self):
    """Test posting to admin setup after initial setup throws an error."""
    super(SetupTest, self).setup_config()

    form_data = {}
    form_data['admin_email'] = FAKE_ADMIN_EMAIL
    form_data['admin_password'] = FAKE_ADMIN_PASSWORD

    resp = self.client.post(flask.url_for('setup_admin'), data=form_data)

    json_response = json.loads(resp.data[len(ufo.XSSI_PREFIX):])
    self.assertEquals(403, json_response['code'])
    self.assertEquals(setup.CANT_SET_ADMIN_AFTER_INITIAL_SETUP,
                      json_response['message'])

  def testPostAdminSetupGoesThrough(self):
    """Test posting to admin setup creates initial admin for configuration."""
    config = models.Config.query.get(0)
    self.assertIsNone(config)

    form_data = {}
    form_data['admin_email'] = FAKE_ADMIN_EMAIL
    form_data['admin_password'] = FAKE_ADMIN_PASSWORD

    resp = self.client.post(flask.url_for('setup_admin'), data=form_data)

    config = models.Config.query.get(0)
    self.assertIsNotNone(config)
    self.assertTrue(config.isConfigured)

    json_response = json.loads(resp.data[len(ufo.XSSI_PREFIX):])
    self.assertEquals(True, json_response['shouldRedirect'])

if __name__ == '__main__':
  unittest.main()
