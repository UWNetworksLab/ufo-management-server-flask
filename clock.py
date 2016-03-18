"""This module schedules all the periodic batch processes on heroku.

https://devcenter.heroku.com/articles/clock-processes-python
"""
# Use the default import to avoid module AttributeError (http://goo.gl/YM7kyZ)
from apscheduler.schedulers.blocking import BlockingScheduler

import ufo
from ufo.services import key_distributor
from ufo.services import user_synchronizer


SCHEDULER = BlockingScheduler()

@SCHEDULER.scheduled_job('interval', minutes=15)
def distribute_user_keys_to_proxy_servers():
  """Schedule the user key distribution to proxy servers."""
  ufo.app.logger.info('Scheduling key distribution to proxy server.')
  key_distributor_service = key_distributor.KeyDistributor()
  key_distributor_service.enqueue_key_distribution_jobs()

@SCHEDULER.scheduled_job('interval', minutes=15)
def sync_users():
  """Schedule the user sync job."""
  ufo.app.logger.info('Scheduling user sync.')
  user_sync_service = user_sync.UserSynchronizer()
  user_sync_service.enqueue_user_sync()


SCHEDULER.start()
