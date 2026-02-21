import os
import redis
from rq import SimpleWorker as Worker, Queue
from dotenv import load_dotenv
from app import create_app
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
redis_conn = redis.from_url(f"{REDIS_URL}")

listen = ["default"]
queues = [Queue(name, connection=redis_conn) for name in listen]

app = create_app()

if __name__ == "__main__":
    with app.app_context(): 
        worker = Worker(queues, connection=redis_conn)
        worker.work()