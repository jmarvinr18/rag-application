import redis
from flask import current_app

redis_client = None

def init_redis(app):
    global redis_client

    redis_client = redis.Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=app.config["REDIS_DB"],
        decode_responses=True
    )
