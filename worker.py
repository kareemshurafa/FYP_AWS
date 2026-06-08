import os
import redis
from rq import Worker, Queue, Connection
from dotenv import load_dotenv
from urllib.parse import urlparse

local = False
if local:
    load_dotenv()

listen = ['high', 'default', 'low']

# redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

# conn = redis.from_url(redis_url)

# Reference - https://devcenter.heroku.com/articles/connecting-heroku-redis#connecting-in-python
url = urlparse(os.environ.get("REDIS_URL"))
conn = redis.Redis(host=url.hostname, port=url.port, password=url.password, ssl=(url.scheme == "rediss"), ssl_cert_reqs=None)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()