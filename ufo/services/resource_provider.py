"""Resource provider module to set resource dictionaries for all pages."""

import flask
import json

import ufo
from ufo.services import regex


def _get_resources():
  """Get the resources for all UI components that need to be shared.

    This dictionary of resources is returned as one large blob for the time
    being to simplify passing all these parameters to the UI. These could be
    separated out again, but they are left as one blob since some are shared
    by multiple Polymer elements and this blob isn't as large as the i18n
    messages. Overall, whether this is one dictionary or multiple, they are
    set within the session regardless of whether they are used, so they all
    get loaded during a request, though perhaps not parsed out on the client
    side.

    Returns:
      A dict of the resources for UI components.
  """
  return {
    'searchPageUrl': flask.url_for('search_page'),
    'searchJsonUrl': flask.url_for('search'),
    'userAddIconUrl': flask.url_for('static', filename='img/add-users.svg'),
    'logoutUrl': flask.url_for('logout'),
    'settingsUrl': flask.url_for('setup') + '#settingsDisplayTemplate',
    'listAdminUrl': flask.url_for('admin_list'),
    'addAdminUrl': flask.url_for('add_admin'),
    'changeAdminPasswordUrl': flask.url_for('change_admin_password'),
    'removeAdminUrl': flask.url_for('delete_admin'),
    'loginUrl': flask.url_for('login'),
    'recaptchaKey': ufo.app.config.get('RECAPTCHA_SITE_KEY', ''),
    'setupUrl': flask.url_for('setup'),
    'setupAdminUrl': flask.url_for('setup_admin'),
    'setupOauthUrl': flask.url_for('setup_oauth'),
    'download_chrome_policy': flask.url_for('download_chrome_policy'),
    'policy_filename': 'chrome_policy.json',
    'proxyServerAddUrl': flask.url_for('proxyserver_add'),
    'proxyServerAddIconUrl': flask.url_for('static',
                                           filename='img/add-servers.svg'),
    'proxyServerInverseAddIconUrl': flask.url_for(
        'static', filename='img/add-servers-inverse.svg'),
    'proxyServerListId': 'proxyList',
    'proxyServerListUrl': flask.url_for('proxyserver_list'),
    'listLimit': 10,
    'proxyServerDetailsButtonId': 'serverDetailsButton',
    'editButtonId': 'serverEditButton',
    'proxyServerDetailsOverlayId': 'serverDetailsOverlay',
    'proxyServerEditUrl': flask.url_for('proxyserver_edit'),
    'proxyServerDeleteUrl': flask.url_for('proxyserver_delete'),
    'proxyServerIconUrl': flask.url_for('static', filename='img/server.svg'),
    'proxyServerAddButtonId': 'addServerButton',
    'proxyServerModalId': 'serverModal',
    'textAreaMaxRows': 10,
    'ipInput': 'ipInput',
    'nameInput': 'nameInput',
    'sshPrivateKeyInput': 'sshPrivateKeyInput',
    'hostPublicKeyInput': 'hostPublicKeyInput',
    'getSettingsUrl': flask.url_for('get_settings'),
    'settingsEditUrl': flask.url_for('edit_settings'),
    'userAddUrl': flask.url_for('add_user'),
    'userInverseAddIconUrl': flask.url_for(
        'static', filename='img/add-users-inverse.svg'),
    'userListId': 'userList',
    'userListUrl': flask.url_for('user_list'),
    'revokeToggleUrl': flask.url_for('user_toggle_revoked'),
    'rotateKeysUrl': flask.url_for('user_get_new_key_pair'),
    'inviteCodeUrl': flask.url_for('user_get_invite_code'),
    'userDeleteUrl': flask.url_for('delete_user'),
    'userDetailsButtonId': 'userDetailsButton',
    'userDetailsOverlayId': 'userDetailsOverlay',
    'userIconUrl': flask.url_for('static', filename='img/user.svg'),
    'userAddButtonId': 'addUserButton',
    'userModalId': 'userModal',
    'groupAddTabId': 'groupAddTab',
    'groupAddFormId': 'groupAdd',
    'groupAddInputName': 'group_key',
    'userAddTabId': 'userAddTab',
    'userAddFormId': 'userAdd',
    'userAddInputName': 'user_key',
    'domainAddTabId': 'domainAddTab',
    'domainAddFormId': 'domainAdd',
    'manualAddTabId': 'manualAddTab',
    'manualAddFormId': 'manualAdd',
    'regexes': regex.REGEXES_AND_ERRORS_DICTIONARY,
    'jsonPrefix': ufo.XSSI_PREFIX,
    'maxFailedLoginsBeforeRecaptcha': ufo.MAX_FAILED_LOGINS_BEFORE_RECAPTCHA,
    'userAddListFlipperId': 'userAddListFlipper',
    'proxyServerAddListFlipperId': 'proxyServerAddListFlipper',
    'userAddTabsId': 'userAddTabs',
    'proxyServerAddFormId': 'serverAddFormHolder',
  }

def set_jinja_globals():
  """Set the jinja global environment to contain all the resource dicts."""

  # The resource keys will not be present.
  ufo.app.logger.info('Start setting resources into jinja globals.\n'
                      'Current jinja globals: %s' %
                      ufo.app.jinja_env.globals.keys())

  ufo.app.jinja_env.globals['resources'] = json.dumps(_get_resources())

  # The resource keys should be present if set.
  ufo.app.logger.info('Finished setting resources into jinja globals.\n'
                      'Current jinja globals: %s' %
                      ufo.app.jinja_env.globals.keys())
