"""This module schedules all the periodic batch processes on heroku.

https://devcenter.heroku.com/articles/clock-processes-python

We will not enqueue background jobs in order to save the extra configuration
and cost to upgrade to Hobby level of service on Heroku.
"""
import logging

# Use the default import to avoid module AttributeError (http://goo.gl/YM7kyZ)
from apscheduler.schedulers.blocking import BlockingScheduler

import ufo
from ufo.services import key_distributor
from ufo.services import user_synchronizer


# http://stackoverflow.com/questions/28724459/no-handlers-could-be-found-for-logger-apscheduler-executors-default
logging.basicConfig()

SCHEDULER = BlockingScheduler()

# TODO: Change the interval back to something that's more acceptable for
# production when TT is done.
@SCHEDULER.scheduled_job('interval', minutes=2)
def schedule_user_key_distribution():
  """Schedule the user key distribution to proxy servers."""
  ufo.app.logger.info('Scheduling key distribution to proxy server.')
  key_distributor_service = key_distributor.KeyDistributor()
  key_distributor_service.start_key_distribution()

@SCHEDULER.scheduled_job('interval', minutes=15)
def schedule_user_sync():
  """Schedule the user sync job."""
  ufo.app.logger.info('Scheduling user sync.')
  user_sync_service = user_synchronizer.UserSynchronizer()
  user_sync_service.sync_db_users_against_directory_service()


SCHEDULER.start()
