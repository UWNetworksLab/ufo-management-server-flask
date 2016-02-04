"""The module for creating workers to process background jobs.

Based on the heroku guide:
https://devcenter.heroku.com/articles/python-rq

See "Queuing jobs" section on how to enqueue jobs.
https://devcenter.heroku.com/articles/python-rq#queuing-jobs

The worker does not start by default after deployment.  It will be necessary
to start manually such as:
heroku ps:scale worker=N
where N is the number of workers that you want.
"""

import os

import redis
from rq import Connection
from rq import Queue
from rq import Worker


listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)


if __name__ == '__main__':
  with Connection(conn):
    worker = Worker(map(Queue, listen))
    worker.work()
