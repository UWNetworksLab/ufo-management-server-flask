import proxy_server

from apscheduler.schedulers.blocking import BlockingScheduler


scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', minutes=15)
def distribute_user_keys_to_proxy_servers():
  """Schedule the user key distribution to proxy servers."""
  print 'Start scheduling key distribution to proxy servers.'
  proxy_server.distribute_keys()
  print 'Finished scheduling key distribution to proxy servers.'

scheduler.start()
