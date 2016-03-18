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


LISTEN = ['high', 'default', 'low']

REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

CONN = redis.from_url(REDIS_URL)


if __name__ == '__main__':
  with Connection(CONN):
    worker = Worker(map(Queue, LISTEN))
    worker.work()
