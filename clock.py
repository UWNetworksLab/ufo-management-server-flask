"""This module schedules all the periodic batch processes on heroku.

https://devcenter.heroku.com/articles/clock-processes-python
"""
# Use the default import to avoid module AttributeError (http://goo.gl/YM7kyZ)
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import ufo


SCHEDULER = BlockingScheduler()

@SCHEDULER.scheduled_job('interval', minutes=15)
def distribute_user_keys_to_proxy_servers():
  """Schedule the user key distribution to proxy servers."""
  # TODO: Configure the logger to direct to stdout.
  print 'Start distributing user keys to proxy server.'
  ufo.proxy_server.distribute_keys()


SCHEDULER.start()
