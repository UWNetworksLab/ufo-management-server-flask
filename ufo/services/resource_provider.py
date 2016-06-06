"""Resource provider module to set resource dictionaries for all pages."""

import flask
import json

import ufo
from ufo.services import regex


def _get_landing_resources():
  """Get the resources for the general landing component.

    Returns:
      A dict of the resources for the general landing component.
  """
  return {
    'searchPageUrl': flask.url_for('search_page'),
    'searchJsonUrl': flask.url_for('search'),
    'userAddIconUrl': flask.url_for('static', filename='img/add-users.svg'),
    'addAdminText': 'Add an Admin',
    'changeAdminPasswordText': 'Change Your Password',
    'removeAdminText': 'Remove an Admin',
    'settingsText': 'Settings',
    'logoutText': 'Log Out',
    'logoutUrl': flask.url_for('logout'),
    'settingsUrl': flask.url_for('setup') + '#settingsDisplayTemplate',
    'listAdminUrl': flask.url_for('admin_list'),
    'addAdminUrl': flask.url_for('add_admin'),
    'adminEmailLabel': 'Admin Email',
    'adminPasswordlabel': 'Admin Password',
    'addAdminSubmitText': 'Add Admin',
    'adminListGetError': ('Error: Getting the list of admins failed. Try '
                          'again later.'),
    'adminExistsError': ('Error: An admin with the specified email already '
                         'exists.'),
    'adminAddSuccessText': 'Success! The specified admin was added.',
    'adminAddFailureText': ('Error: Adding the specified admin failed. Try '
                            'again later.'),
    'changeAdminPasswordUrl': flask.url_for('change_admin_password'),
    'changeAdminPasswordInstructions': ('Enter your current password and a ' +
                                        'new one then submit to update it.'),
    'changeAdminPasswordOldLabel': 'Current Password',
    'changeAdminPasswordNewLabel': 'New Password',
    'changeAdminPasswordSubmitText': 'Update Password',
    'removeAdminUrl': flask.url_for('delete_admin'),
    'removeAdminInstructions': 'Select an Admin below by email to remove.',
    'removeAdminSubmitText': 'Remove Admin',
    'errorTitleText': 'Something is Not Right',
    'closeText': 'Close',
    'regexes': regex.REGEXES_AND_ERRORS_DICTIONARY,
    'jsonPrefix': ufo.XSSI_PREFIX,
  }

def _get_login_resources():
  """Get the resources for the login component.

    Returns:
      A dict of the resources for the login component.
  """
  return {
    'loginTitleText': 'Please Log In',
    'loginUrl': flask.url_for('login'),
    'emailLabel': 'Email',
    'passwordLabel': 'Password',
    'loginText': 'Login',
    'regexes': regex.REGEXES_AND_ERRORS_DICTIONARY,
    'jsonPrefix': ufo.XSSI_PREFIX,
    'recaptchaKey': ufo.app.config['RECAPTCHA_SITE_KEY'],
  }

def _get_oauth_resources():
  """Get the resources for the oauth component.

    Returns:
      A dict of the resources for the oauth component.
  """
  return {
    'setup_url': flask.url_for('setup'),
    'oauthTitleText': 'Oauth Configuration',
    'welcomeText': ('Hey there! Welcome to the uProxy for Organizations '
        'management server! To start, we want to get a bit of information '
        'from you to get everything set up.'),
    'googleDomainPromptText': ('First of all, if you are planning on using '
        'this application with a Google apps domain, we\'re going to need to '
        'get permission from you to access that. This will be used to keep '
        'the list of users in your domain in sync with who is allowed to '
        'access the uProxy servers. The credentials you authorize will be '
        'shared by any administrators who log into this server. If you do not '
        'plan on using a Google apps domain with this product, you can just '
        'go straight to adding users.'),
    'successSetupText': ('You have already successfully configured this '
        'deployment! If you want to change the settings, you may do so below. '
        'Please note: submitting the form even without filling in any '
        'parameters will cause the previous saved configuration to be lost.'),
    'domainConfiguredText': ('This site is set up to work with the following '
        'domain. If that is not correct, please update the configuration.'),
    'noDomainConfiguredText': ('This site is not set up to use any Google '
        'apps domain name. All users will need to be manually input.'),
    'betaWarningText': ('Please keep in mind that this is a much simpler '
        'version than what you would actually expect to see in a finished '
        'version of the site. Noteably, this page should include something '
        'about authenticating yourself in the future (and actually include a '
        'way to skip).'),
    'connectYourDomainButtonText': 'Connect to Your Domain',
    'pasteTheCodeText': ('Once you finish authorizing access, please paste '
        'the code you receive in the box below.'),
    'adminEmailLabel': 'Admin Email',
    'adminPasswordlabel': 'Admin Password',
    'submitButtonText': 'Submit',
    'jsonPrefix': ufo.XSSI_PREFIX,
  }

def _get_policy_resources():
  """Get the resources for the chrome policy component.

    Returns:
      A dict of the resources for the chrome policy component.
  """
  return {
    'download_chrome_policy': flask.url_for('download_chrome_policy'),
    'policy_filename': 'chrome_policy.json',
    'chromePolicyTitleText': 'Chrome Policy',
    'policyExplanationText': ('Chrome policy is a feature of enterprise '
        'Google devices which can be used to securely add extra configuration '
        'to the uProxy frontend. If you use enterprise Google devices through '
        'Google Apps for Work, you can for example turn on validation for '
        'invitation links to ensure you are proxying through an endpoint '
        'controlled by the management console.'),
    'policyEditText': ('You can adjust the values below in the Management '
        'Server Settings section and save to update the managed policy json.'
        'Once you are ready, you can click the download link to get your json '
        'policy file generated automatically.'),
    'adminConsoleText': 'Google Admin Console',
    'policyUploadText': ('To push your managed policy out to your devices, '
        'visit Google Admin Console at the link above and navigate to the '
        'uProxy Chrome App/Extension under Device Management -> Chrome '
        'Management -> App Management. For the App and Extension, select the '
        'entry listed, then click User settings. From the list of Orgs, '
        'choose which you want the policy to apply to, then enable Force '
        'Installation and select Upload Configuration File. Choose the json '
        'file you just downloaded. You may have to click override to edit '
        'Force Installation or Configure\'s values. Finally, click Save.'),
    'downloadText': 'Download',
    'jsonPrefix': ufo.XSSI_PREFIX,
  }


def _get_proxy_server_resources():
  """Get the resources for the proxy server component.

    Returns:
      A dict of the resources for the proxy server component.
  """
  return {
    'proxyServerAddUrl': flask.url_for('proxyserver_add'),
    'proxyServerAddIconUrl': flask.url_for('static',
                                           filename='img/add-servers.svg'),
    'proxyServerInverseAddIconUrl': flask.url_for(
        'static', filename='img/add-servers-inverse.svg'),
    'proxyServerAddText': 'Add a Server',
    'proxyServerListId': 'proxyList',
    'proxyServerListUrl': flask.url_for('proxyserver_list'),
    'listLimit': 10,
    'proxyServerDetailsExpandText': 'Expand Server',
    'closeText': 'Close',
    'proxyServerDetailsButtonId': 'serverDetailsButton',
    'editButtonId': 'serverEditButton',
    'proxyServerDetailsOverlayId': 'serverDetailsOverlay',
    'editText': 'Edit',
    'saveText': 'Save',
    'proxyServerDeleteLabel': 'Delete Server',
    'proxyServerEditUrl': flask.url_for('proxyserver_edit'),
    'proxyServerDeleteUrl': flask.url_for('proxyserver_delete'),
    'proxyServerSeeAllText': 'See All Servers',
    'proxyServerTitleText': 'Servers',
    'nameColumnHeader': 'Name',
    'ipColumnHeader': 'IP Address',
    'modfyColumnHeader': 'Modify',
    'proxyServerIconUrl': flask.url_for('static', filename='img/server.svg'),
    'proxyServerAddButtonId': 'addServerButton',
    'proxyServerModalId': 'serverModal',
    'dismissText': 'Cancel',
    'confirmText': 'Add Server',
    'regexes': regex.REGEXES_AND_ERRORS_DICTIONARY,
    'jsonPrefix': ufo.XSSI_PREFIX,
    'textAreaMaxRows': 10,
    'ipLabel': 'IP Address',
    'nameLabel': 'Server Name',
    'sshPrivateKeyLabel': 'SSH Private Key',
    'hostPublicKeyLabel': 'Host Public Key',
    'ipInput': 'ipInput',
    'nameInput': 'nameInput',
    'sshPrivateKeyInput': 'sshPrivateKeyInput',
    'hostPublicKeyInput': 'hostPublicKeyInput',
    'ip_address': '',
    'name': '',
    'ssh_private_key': '',
    'host_public_key': '',
    'sshPrivateKeyText': (
        'For the private key, please copy the full contents of '
        'a private key file with the ability to access a proxy '
        'server. This key is used by the ssh client. '
        'The beginning of the file should resemble '
        '"-----BEGIN RSA PRIVATE KEY-----".'),
    'hostPublicKeyText': (
        'For the public key, you can usually get this value from '
        '/etc/ssh/ssh_host_rsa_key.pub of the proxy server. '
        'This public key is used to authenticate the proxy server.'),
    'rsaText': ('For now, please be sure to use an RSA key (the text should '
                'begin with ssh-rsa)'),
  }

def _get_settings_resources():
  """Get the resources for the settings configuration component.

    Returns:
      A dict of the resources for the settings configuration component.
  """
  return {
    'settingsTitleText': 'Management Server Settings',
    'getSettingsUrl': flask.url_for('get_settings'),
    'settingsEditUrl': flask.url_for('edit_settings'),
    'proxyValidityText': 'Enforce Proxy Server Check from Invitation Link',
    'networkJailText': 'Enforce Network Jail Before Google Login',
    'saveText': 'Save',
    'jsonPrefix': ufo.XSSI_PREFIX,
  }

def _get_user_resources():
  """Get the resources for the user component(s).

    Returns:
      A dict of the resources for the user component(s).
  """
  return {
    'userAddUrl': flask.url_for('add_user'),
    'userAddIconUrl': flask.url_for('static', filename='img/add-users.svg'),
    'userInverseAddIconUrl': flask.url_for(
        'static', filename='img/add-users-inverse.svg'),
    'userAddText': 'Add Users',
    'lookAgainText': 'Search Again',
    'userListId': 'userList',
    'userListUrl': flask.url_for('user_list'),
    'listLimit': 10,
    'revokeToggleUrl': flask.url_for('user_toggle_revoked'),
    'rotateKeysUrl': flask.url_for('user_get_new_key_pair'),
    'inviteCodeUrl': flask.url_for('user_get_invite_code'),
    'userDeleteUrl': flask.url_for('delete_user'),
    'userDetailsExpandText': 'Expand User',
    'closeText': 'Close',
    'userDetailsButtonId': 'userDetailsButton',
    'userDetailsOverlayId': 'userDetailsOverlay',
    'inviteCodeNeedServerText': ('Invite codes aren\'t available without any '
                                 'proxy server configured. Configure a proxy '
                                 'server to have an invite code created '
                                 'automatically.'),
    'inviteCodeLabel': 'Invite Code',
    'privateKeyLabel': 'SSH Private Key',
    'publicKeyLabel': 'SSH Public Key',
    'copyLabel': 'Copy Code',
    'rotateKeysLabel': 'Create New Code',
    'userDeleteLabel': 'Delete User',
    'userSeeAllText': 'See All Users',
    'userTitleText': 'Users',
    'nameColumnHeader': 'Name',
    'emailColumnHeader': 'Email',
    'accessColumnHeader': 'Access',
    'userIconUrl': flask.url_for('static', filename='img/user.svg'),
    'userAddButtonId': 'addUserButton',
    'userModalId': 'userModal',
    'dismissText': 'Cancel',
    'regexes': regex.REGEXES_AND_ERRORS_DICTIONARY,
    'jsonPrefix': ufo.XSSI_PREFIX,
    'addFlowNoResults': 'No results found.',
    'groupAddTabId': 'groupAddTab',
    'groupAddTab': 'Search for Users in Group',
    'groupAddFormId': 'groupAdd',
    'groupAddSearchButton': 'Search for Users in Group',
    'groupAddEmailAddressLabel': 'Group Email Address',
    'groupAddInputName': 'group_key',
    'groupAddEmailAddressDefinition': ('To add users by group, please provide '
                                       'a valid group email address or unique '
                                       'id.'),
    'userAddTabId': 'userAddTab',
    'userAddTab': 'Search for Individual Users',
    'userAddFormId': 'userAdd',
    'userAddSearchButton': 'Search for Individual User',
    'userAddEmailAddressLabel': 'Email Address',
    'userAddInputName': 'user_key',
    'userAddEmailAddressDefinition': ('To add individual users, please '
                                      'provide a valid email address or '
                                      'unique id.'),
    'domainAddTabId': 'domainAddTab',
    'domainAddTab': 'View All Users in the Domain',
    'domainAddFormId': 'domainAdd',
    'domainAddSearchButton': 'Search for Users in Domain',
    'manualAddTabId': 'manualAddTab',
    'manualAddTab': 'Add Manually',
    'manualAddFormId': 'manualAdd',
    'manualFullNameLabel': 'Full Name',
    'manualEmailAddressLabel': 'Email Address',
    'saveMultipleUsersButton': 'Add Users',
    'saveIndividualUserButton': 'Add User',
  }

def set_jinja_globals():
  """Set the jinja global environment to contain all the resource dicts."""

  # The resource keys will not be present.
  ufo.app.logger.info('Start setting resources into jinja globals.\n'
                      'Current jinja globals: %s' %
                      ufo.app.jinja_env.globals.keys())

  ufo.app.jinja_env.globals['landing_resources'] = json.dumps(
      _get_landing_resources())
  ufo.app.jinja_env.globals['login_resources'] = json.dumps(
      _get_login_resources())
  ufo.app.jinja_env.globals['oauth_resources'] = json.dumps(
      _get_oauth_resources())
  ufo.app.jinja_env.globals['policy_resources'] = json.dumps(
      _get_policy_resources())
  ufo.app.jinja_env.globals['proxy_server_resources'] = (
      json.dumps(_get_proxy_server_resources()))
  ufo.app.jinja_env.globals['settings_resources'] = json.dumps(
      _get_settings_resources())
  ufo.app.jinja_env.globals['user_resources'] = json.dumps(
      _get_user_resources())

  # The resource keys should be present if set.
  ufo.app.logger.info('Finished setting resources into jinja globals.\n'
                      'Current jinja globals: %s' %
                      ufo.app.jinja_env.globals.keys())
