"""This module schedules all the periodic batch processes on heroku.

https://devcenter.heroku.com/articles/clock-processes-python
"""
import apscheduler
import ufo


SCHEDULER = apscheduler.schedulers.blocking.BlockingScheduler()

@SCHEDULER.scheduled_job('interval', minutes=15)
def distribute_user_keys_to_proxy_servers():
  """Schedule the user key distribution to proxy servers."""
  # TODO: Get rid of the print by having a logger that redirects to stdout.
  print 'Start scheduling key distribution to proxy servers.'
  ufo.proxy_server.distribute_keys()
  print 'Finished scheduling key distribution to proxy servers.'

SCHEDULER.start()
