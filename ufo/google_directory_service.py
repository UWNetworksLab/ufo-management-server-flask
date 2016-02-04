"""Module to interact with Google Directory API."""

import httplib2

from googleapiclient import discovery

import ufo.models

NUM_RETRIES = 3

VALID_WATCH_EVENTS = ['add', 'delete', 'makeAdmin', 'undelete', 'update']

# TODO(eholder): Write tests for these functions.

class GoogleDirectoryService(object):

  """Interact with Google Directory API."""

  def __init__(self, credentials):
    """Create a service object for admin directory services using oauth."""
    self.service = discovery.build(serviceName='admin',
                                   version='directory_v1',
                                   http=credentials.authorize(httplib2.Http()))

  def GetUsers(self):
    """Get the users of a domain.

    Returns:
      A list of users.

    Raises:
      googleapiclient.errors.HttpError on failure to find the domain.
    """
    config = ufo.models.Config.query.get(0)
    users = []
    page_token = ''
    while True:
      request = self.service.users().list(domain=config.domain,
                                          maxResults=500,
                                          pageToken=page_token,
                                          projection='full',
                                          orderBy='email')
      result = request.execute(num_retries=NUM_RETRIES)
      users += result['users']
      if 'nextPageToken' in result:
        page_token = result['nextPageToken']
      else:
        break

    return users

  def GetUsersByGroupKey(self, group_key):
    """Get the users belonging to a group.

    Args:
      group_key: A string identifying a google group for querying users.

    Returns:
      A list of group members which are users and not groups.

    Raises:
      googleapiclient.errors.HttpError on failure to find the group.
    """
    users = []
    members = []
    page_token = ''
    while True:
      if page_token is '':
        request = self.service.members().list(groupKey=group_key)
      else:
        request = self.service.members().list(groupKey=group_key,
                                              pageToken=page_token)
      result = request.execute(num_retries=NUM_RETRIES)
      members += result['members']
      if 'nextPageToken' in result:
        page_token = result['nextPageToken']
      else:
        break

    user = 'USER'
    # Limit to only users, not groups
    for member in members:
      if 'type' in member and member['type'] == user and member['id']:
        users.append(self.GetUser(member['id']))

    return users

  def GetUser(self, user_key):
    """Get a user based on a user key.

    Args:
      user_key: A string identifying an individual user.

    Returns:
      The user if found.

    Raises:
      googleapiclient.errors.HttpError on failure to find the user.
    """
    request = self.service.users().get(userKey=user_key, projection='full')
    result = request.execute(num_retries=NUM_RETRIES)

    return result

  def GetUserAsList(self, user_key):
    """Get a user based on a user key.

    List format is used here for consistency with the other methods and to
    simplify rendering a template based on the response.

    Args:
      user_key: A string identifying an individual user.

    Returns:
      A list with that user in it or empty.

    Raises:
      googleapiclient.errors.HttpError on failure to find the user.
    """
    users = []
    result = self.GetUser(user_key)
    if result['primaryEmail']:
      users.append(result)

    return users

  def IsAdminUser(self, user_key):
    """Check if a given user is an admin according to the directory API.

    Args:
      user_key: A string identifying an individual user.

    Returns:
      True or false for whether or not the user is or is not an admin.

    Raises:
      googleapiclient.errors.HttpError on failure to find the user.
    """
    result = self.GetUser(user_key)
    return result['isAdmin']
