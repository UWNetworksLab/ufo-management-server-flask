"""This module schedules all the periodic batch processes on heroku.

https://devcenter.heroku.com/articles/clock-processes-python
"""
# Use the default import to avoid module AttributeError (http://goo.gl/YM7kyZ)
from apscheduler.schedulers.blocking import BlockingScheduler
import ufo
from ufo import app


SCHEDULER = BlockingScheduler()

@SCHEDULER.scheduled_job('interval', minutes=15)
def distribute_user_keys_to_proxy_servers():
  """Schedule the user key distribution to proxy servers."""
  app.logger.info('Scheduling key distribution to proxy server.')
  key_distributor = ufo.key_distributor.KeyDistributor()
  key_distributor.enqueue_key_distribution_jobs()


SCHEDULER.start()
