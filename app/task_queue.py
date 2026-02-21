# app/task_queue.py
import os
import redis
from rq import Queue
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
redis_conn = redis.from_url(REDIS_URL)

# default queue
task_queue = Queue("default", connection=redis_conn)