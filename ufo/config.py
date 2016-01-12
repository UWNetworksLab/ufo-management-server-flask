"""App configs to simplify the importing for tests and mocks."""


import jinja2
import os
import xsrf

ROOT = os.path.dirname(__file__)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(ROOT),
    extensions=['jinja2.ext.autoescape',
                'jinja2.ext.i18n'],
    autoescape=True)

PATHS = {
    'landing_page_path': '/',
    'user_page_path': '/user',

    'user_add_path': '/user/add',
    'user_delete_path': '/user/delete',
    'user_details_path': '/user/details',
    'user_get_invite_code_path': '/user/getInviteCode',
    'user_get_new_key_pair_path': '/user/getNewKeyPair',
    'user_toggle_revoked_path': '/user/toggleRevoked',

    'setup_oauth_path': '/setup',

    'proxy_server_add': '/proxyserver/add',
    'proxy_server_delete': '/proxyserver/delete',
    'proxy_server_edit': '/proxyserver/edit',
    'proxy_server_list': '/proxyserver/list',

    'cron_proxy_server_distribute_key': '/cron/proxyserver/distributekey',

    'receive_push_notifications': '/receive',
    'sync_top_level_path': '/sync',
    'notification_channels_list': '/sync/channels',
    'notifications_list': '/sync/notifications',
    'watch_for_user_deletion': '/sync/delete',
    'unsubscribe_from_notifications': '/sync/unsubscribe',

    'logout': '/logout',
}

# JINJA_ENVIRONMENT.globals['xsrf_token'] = xsrf.XSRFToken()
# HOST = str(app_identity.get_default_version_hostname())
JINJA_ENVIRONMENT.globals['BASE_URL'] = ('http://0.0.0.0:5000')
JINJA_ENVIRONMENT.globals['EMAIL_VALIDATION_PATTERN'] = r'[^@]+@[^@]+.[^@]+'
email_validation_error = 'Please supply a valid email address.'
JINJA_ENVIRONMENT.globals['EMAIL_VALIDATION_ERROR'] = email_validation_error
# Key lookup for users and group allows email or unique id.
key_lookup_pattern = r'([^@]+@[^@]+.[^@]+|[a-zA-Z0-9]+)'
key_lookup_error = 'Please supply a valid email address or unique id.'
JINJA_ENVIRONMENT.globals['KEY_LOOKUP_VALIDATION_PATTERN'] = key_lookup_pattern
JINJA_ENVIRONMENT.globals['KEY_LOOKUP_VALIDATION_ERROR'] = key_lookup_error

for key, value in PATHS.iteritems():
  JINJA_ENVIRONMENT.globals[key] = value

# Add any libraries installed in the "lib" folder.
# vendor.add('lib')
