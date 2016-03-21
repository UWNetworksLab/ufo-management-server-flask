"""Resource dicts module which provides resource dictionaries for all pages."""

import flask
import json

import ufo
from ufo.services import regex


def get_landing():
  """Get the resources for the general landing component.

    Returns:
      A dict of the resources for the general landing component.
  """
  return {
    'searchPageUrl': flask.url_for('search_page'),
    'searchJsonUrl': flask.url_for('search'),
    'addIconUrl': flask.url_for('static', filename='img/add-users.svg'),
    'addAdminText': 'Add an Admin',
    'settingsText': 'Settings',
    'logoutText': 'Log Out',
    'logoutUrl': flask.url_for('logout'),
  }

def get_login():
  """Get the resources for the login component.

    Returns:
      A dict of the resources for the login component.
  """
  return {
    'hasAddFlow': False,
    'titleText': 'Please Log In',
    'loginUrl': flask.url_for('login'),
    'usernameLabel': 'Username',
    'passwordLabel': 'Password',
    'loginText': 'Login',
  }

def get_oauth():
  """Get the resources for the oauth component.

    Returns:
      A dict of the resources for the oauth component.
  """
  return {
    'hasAddFlow': False,
    'setup_url': flask.url_for('setup'),
    'titleText': 'Oauth Configuration',
    'welcomeText': ('Hey there! Welcome to the uProxy for Organizations '
        'management server! To start, we want to get a bit of information from'
        ' you to get everything set up.'),
    'googleDomainPromptText': ('First of all, if you are planning on using '
        'this application with a Google apps domain, we\'re going to need to '
        'get permission from you to access that. This will be used to keep '
        'the list of users in your domain in sync with who is allowed to '
        'access the uProxy servers. The credentials you authorize will be '
        'shared by any administrators who log into this server. If you do not '
        'plan on using a Google apps domain with this product, you can just go'
        ' straight to adding users.'),
    'successSetupText': ('You have already successfully configured this '
        'deployment! If you want to change the settings, you may do so below. '
        'Please note: submitting the form even without filling in any '
        'parameters will cause the previous saved configuration to be lost.'),
    'domainConfiguredText': ('This site is set up to work with the following '
        'domain. If that is not correct, please update the configuration.'),
    'noDomainConfiguredText': ('This site is not set up to use any Google apps'
        ' domain name. All users will need to be manually input.'),
    'betaWarningText': ('Please keep in mind that this is a much simpler '
        'version than what you would actually expect to see in a finished '
        'version of the site. Noteably, this page should include something '
        'about authenticating yourself in the future (and actually include a '
        'way to skip).'),
    'connectYourDomainButtonText': 'Connect to Your Domain',
    'pasteTheCodeText': ('Once you finish authorizing access, please paste the'
        ' code you receive in the box below.'),
    'submitButtonText': 'Submit',
    }

def get_policy():
  """Get the resources for the chrome policy component.

    Returns:
      A dict of the resources for the chrome policy component.
  """
  return {
    'download_chrome_policy': flask.url_for('download_chrome_policy'),
    'isChromePolicy': True,
    'hasAddFlow': False,
    'policy_filename': 'chrome_policy.json',
    'titleText': 'Chrome Policy',
    'policyExplanationText': ('Chrome policy is a feature of enterprise Google'
        ' devices which can be used to securely add extra configuration to the'
        ' uProxy frontend. If you use enterprise Google devices through Google'
        ' Apps for Work, you can for example turn on validation for invitation'
        ' links to ensure you are proxying through an endpoint controlled by '
        'the management console.'),
    'policyEditText': ('You can adjust the values below in the Management '
        'Server Settings section and save to update the managed policy json.'
        'Once you are ready, you can click the download link to get your json '
        'policy file generated automatically.'),
    'adminConsoleText': 'Google Admin Console',
    'policyUploadText': ('To push your managed policy out to your devices, '
        'visit Google Admin Console at the link above and navigate to the '
        'uProxy Chrome App/Extension under Device Management -> Chrome '
        'Management -> App Management. For the App and Extension, select the '
        'entry listed, then click User settings. From the list of Orgs, choose'
        ' which you want the policy to apply to, then enable Force '
        'Installation and select Upload Configuration File. Choose the json '
        'file you just downloaded. You may have to click override to edit '
        'Force Installation or Configure\'s values. Finally, click Save.'),
    'downloadText': 'Download',
  }


def get_proxy_server(with_add_flow=True):
  """Get the resources for the proxy server component.

    Args:
      with_add_flow: If true, set hasAddFlow to true. Otherwise set to false.

    Returns:
      A dict of the resources for the proxy server component.
  """
  proxy_server_resource_dict = {
    'addUrl': flask.url_for('proxyserver_add'),
    'addIconUrl': flask.url_for('static', filename='img/add-servers.svg'),
    'inverseAddIconUrl': flask.url_for('static', filename='img/add-servers-inverse.svg'),
    'addText': 'Add a Server',
    'listId': 'proxyList',
    'listUrl': flask.url_for('proxyserver_list'),
    'listLimit': 10,
    'detailsButtonText': 'Edit Server',
    'detailsButtonId': 'serverEditButton',
    'detailsOverlayId': 'serverDetailsOverlay',
    'editText': 'Edit',
    'saveText': 'Save',
    'deleteLabel': 'Delete Server',
    'editUrl': flask.url_for('proxyserver_edit'),
    'deleteUrl': flask.url_for('proxyserver_delete'),
    'seeAllText': 'See All Servers',
    'titleText': 'Servers',
    'itemIconUrl': flask.url_for('static', filename='img/server.svg'),
    'isProxyServer': True,
    'hasAddFlow': True,
    'modalId': 'serverModal',
    'dismissText': 'Cancel',
    'confirmText': 'Add Server',
    'regexes': regex.REGEXES_AND_ERRORS_DICTIONARY,
    'textAreaMaxRows': 10,
    'ipLabel': 'IP Address',
    'nameLabel': 'Server Name',
    'privateKeyLabel': 'SSH Private Key',
    'publicKeyLabel': 'SSH Host Public Key',
    'ip_address': '',
    'name': '',
    'private_key': '',
    'public_key': '',
    'privateKeyText': ('For the private key, please copy the full contents of '
                       'a private key file with the ability to access a proxy '
                       'server. The beginning of the file should resemble '
                       '"-----BEGIN RSA PRIVATE KEY-----".'),
    'publicKeyText': ('For the hosts public key, you can usually get this '
                      'value from either /etc/ssh/ssh_host_rsa_key.pub or from'
                      ' the line in $HOME/.ssh/known_hosts on your server.'),
    'rsaText': ('For now, please be sure to use an RSA key (the text should '
                'begin with ssh-rsa)'),
  }
  if not with_add_flow:
    proxy_server_resource_dict['hasAddFlow'] = False

  return proxy_server_resource_dict

def get_settings():
  """Get the resources for the settings configuration component.

    Returns:
      A dict of the resources for the settings configuration component.
  """
  return {
    'hasAddFlow': False,
    'titleText': 'Management Server Settings',
    'getSettingsUrl': flask.url_for('get_settings'),
    'editUrl': flask.url_for('edit_settings'),
    'proxyValidityText': 'Enforce Proxy Server Check from Invitation Link',
    'networkJailText': 'Enforce Network Jail Before Google Login',
    'saveText': 'Save',
  }

def get_user(with_add_flow=True):
  """Get the resources for the user component(s).

    Args:
      with_add_flow: If true, set hasAddFlow to true. Otherwise set to false.

    Returns:
      A dict of the resources for the user component(s).
  """
  user_resource_dict = {
    'addUrl': flask.url_for('add_user'),
    'addIconUrl': flask.url_for('static', filename='img/add-users.svg'),
    'inverseAddIconUrl': flask.url_for('static', filename='img/add-users-inverse.svg'),
    'addText': 'Add Users',
    'lookAgainText': 'Search Again',
    'listId': 'userList',
    'listUrl': flask.url_for('user_list'),
    'listLimit': 10,
    'revokeToggleUrl': flask.url_for('user_toggle_revoked'),
    'rotateKeysUrl': flask.url_for('user_get_new_key_pair'),
    'inviteCodeUrl': flask.url_for('user_get_invite_code'),
    'deleteUrl': flask.url_for('delete_user'),
    'detailsButtonText': 'User Details',
    'detailsButtonId': 'userDetailsButton',
    'detailsOverlayId': 'userDetailsOverlay',
    'inviteCodeLabel': 'Invite Code',
    'privateKeyLabel': 'SSH Private Key',
    'publicKeyLabel': 'SSH Public Key',
    'copyLabel': 'Copy Code',
    'rotateKeysLabel': 'Create New Code',
    'deleteLabel': 'Delete User',
    'seeAllText': 'See All Users',
    'titleText': 'Users',
    'itemIconUrl': flask.url_for('static', filename='img/user.svg'),
    'isUser': True,
    'hasAddFlow': True,
    'modalId': 'userModal',
    'dismissText': 'Cancel',
    'regexes': regex.REGEXES_AND_ERRORS_DICTIONARY,
    'addFlowTextDicts': [
        {
          'id': 'groupAdd',
          'tab': 'Add Group',
          'saveButton': 'Add Group',
          'searchButton': 'Search for Users in Group',
          'label1': 'Group key',
          'definition1': ('To add users by group, please provide a valid '
                          'group email address or unique id.'),
          'name1': 'group_key',
          'isManual': False,
        },
        {
          'id': 'userAdd',
          'tab': 'Add Individual',
          'saveButton': 'Add User',
          'searchButton': 'Search for Specific User',
          'label1': 'User key',
          'definition1': ('To add individual users, please provide a valid '
                          'email address or unique id.'),
          'name1': 'user_key',
          'isManual': False,
        },
        {
          'id': 'domainAdd',
          'tab': 'Add by Domain',
          'saveButton': 'Add Users',
          'searchButton': 'Search for Users in Domain',
          'isManual': False,
        },
        {
          'id': 'manualAdd',
          'tab': 'Add Manually',
          'saveButton': 'Add User',
          'label1': 'Input user name here.',
          'label2': 'Input user email here.',
          'isManual': True,
        },
    ],
  }
  if not with_add_flow:
    user_resource_dict['hasAddFlow'] = False

  return user_resource_dict

def set_jinja_globals():
  """Set the jinja global environment to contain all the resource dicts."""
  ufo.app.jinja_env.globals['landing_resources'] = json.dumps(get_landing())
  ufo.app.jinja_env.globals['login_resources'] = json.dumps(get_login())
  ufo.app.jinja_env.globals['oauth_resources'] = json.dumps(get_oauth())
  ufo.app.jinja_env.globals['policy_resources'] = json.dumps(get_policy())
  ufo.app.jinja_env.globals['proxy_server_resources'] = (
      json.dumps(get_proxy_server()))
  ufo.app.jinja_env.globals['proxy_server_resources_without_add_flow'] = (
      json.dumps(get_proxy_server(with_add_flow=False)))
  ufo.app.jinja_env.globals['settings_resources'] = json.dumps(get_settings())
  ufo.app.jinja_env.globals['user_resources'] = json.dumps(get_user())
  ufo.app.jinja_env.globals['user_resources_without_add_flow'] = (
      json.dumps(get_user(with_add_flow=False)))
