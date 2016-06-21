"""The module for syncing user periodically from google directory service."""

from rq import Queue

import ufo
from ufo.database import models
from ufo.services import google_directory_service
from ufo.services import oauth
import worker


class UserSynchronizer(object):
  """Syncs users in the db's status with Google directory service."""

  def enqueue_user_sync(self):
    """Check users currently in the DB are still valid in directory service."""
    ufo.app.logger.info('Enqueuing cron user sync job.')
    queue = Queue(connection=worker.CONN)
    queue.enqueue(self.sync_db_users_against_directory_service)

  def sync_db_users_against_directory_service(self):
    """Checks whether the users currently in the DB are still valid.

    This gets all users in the DB, finds those that match the current domain,
    and compares them to those found in the domain in Google Directory Service.
    If a user in the DB is not the domain, then it is presumed to be deleted
    and will thus be removed from our DB.
    """
    db_users = models.User.query.all()
    directory_users = {}
    config = ufo.get_user_config()
    with ufo.app.app_context():
      credentials = oauth.getSavedCredentials()
      # TODO this should handle the case where we do not have oauth
      if not credentials:
        ufo.app.logger.info('OAuth credentials not set up. Can\'t sync users.')
        return

      try:
        directory_service = google_directory_service.GoogleDirectoryService(
            credentials)
        directory_users = directory_service.GetUsersAsDictionary()

      except errors.HttpError as error:
        ufo.app.logger.info('Error encountered while requesting users from '
                            'directory service: ' + str(error))
        return

      for db_user in db_users:
        # Don't worry about users from another domain since they won't show up.
        if db_user.domain != config.domain:
          ufo.app.logger.info('User ' + db_user.email + ' did not match the  '
                              'current domain. Ignoring in directory service.')
          continue

        # Lookup user in dictionary based on email field.
        directory_user = directory_users.get(db_user.email, None)

        # TODO(eholder): Unit test the conditionals here.
        # Assume deleted if not found, so delete from our db.
        if directory_user is None:
          ufo.app.logger.info('User ' + db_user.email + ' was not found in '
                              'directory service.')
          self.perform_configured_action_on_user(config.user_delete_action,
                                                 db_user)
          continue

        if directory_user['suspended']:
          ufo.app.logger.info('User ' + db_user.email + ' was suspended in '
                              'directory service.')
          self.perform_configured_action_on_user(config.user_revoke_action,
                                                 db_user)
          continue

  def perform_configured_action_on_user(self, action, user):
    """Perform the database configured action given on the specified user.

    Args:
      action: A string representing the action from the database.
      user: A user entity from the database to perform the configured action
            upon.
    """
    if action == models.CRON_JOB_ACTIONS['delete']:
      ufo.app.logger.info('Deleting ' + user.email + ' from database.')
      user.delete()
    elif action == models.CRON_JOB_ACTIONS['revoke']:
      ufo.app.logger.info('Revoking access from ' + user.email + '.')
      user.is_key_revoked = True
      user.did_cron_revoke = True
      user.save()
