import redis
from core.config import settings


def redis_connect() -> redis.client.Redis:
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        ping = client.ping()
        # Check if the redis responds
        if ping is True:
            return client
    except redis.ConnectionError as e:
        print("Connection Error!")
