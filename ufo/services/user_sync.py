"""The module for syncing user periodically from google directory service."""

from rq import Queue

import ufo
from ufo.database import models
from ufo.services import google_directory_service
from ufo.services import oauth
import worker


def _check_db_users_against_directory_service():
  """Checks whether the users currently in the DB are still valid.

  This gets all users in the DB, finds those that match the current domain,
  and compares them to those found in Google Directory Service for the domain.
  If a user in the DB is not the domain, then it is presumed to be deleted and
  will thus be removed from our DB.
  """
  db_users = models.User.query.all()
  config = ufo.get_user_config()
  credentials = oauth.getSavedCredentials()
  # TODO this should handle the case where we do not have oauth
  if not credentials:
    ufo.app.logger.info('OAuth credentials not set up. Can\'t sync users.')

  directory_users = {}
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
    directory_user = directory_users.get(db_user.email, default=None):
    print 'Found user: ' + str(directory_user)

    # Assume deleted if not found, so delete from our db.
    if directory_user is None:
      if config.user_delete_action is models.CRON_JOB_ACTIONS['delete']:
        ufo.app.logger.info('User ' + db_user.email + ' was not found in '
                            'directory service. Deleting from database.')
        db_user.delete()
      elif config.user_delete_action is models.CRON_JOB_ACTIONS['revoke']:
        ufo.app.logger.info('User ' + db_user.email + ' was not found in '
                            'directory service. Revoking access.')
        db_user.is_key_revoked = True
        db_user.did_cron_revoke = True
        db_user.save()
      continue

    if directory_user['suspended']:
      if config.user_revoke_action is models.CRON_JOB_ACTIONS['delete']:
        ufo.app.logger.info('User ' + db_user.email + ' was suspended in '
                            'directory service. Deleting from database.')
        db_user.delete()
      elif config.user_revoke_action is models.CRON_JOB_ACTIONS['revoke']:
        ufo.app.logger.info('User ' + db_user.email + ' was suspended in '
                            'directory service. Revoking access.')
        db_user.is_key_revoked = True
        db_user.did_cron_revoke = True
        db_user.save()
      continue

  def enqueue_user_sync():
    """Check users currently in the DB are still valid in directory service."""
    ufo.app.logger.info('Enqueuing cron user sync job.')
    queue = Queue(connection=worker.CONN)
    queue.enqueue(_check_db_users_against_directory_service)
