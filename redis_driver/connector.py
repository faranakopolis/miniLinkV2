from typing import Union

from redis_driver.redis import redis_connect


def set_url(original_url: str, hashed_url: str) -> bool:
    try:
        # Store the hashed -> original key-value in redis
        redis_client = redis_connect()
        redis_client.set(hashed_url, original_url)
        redis_client.save()
        return True
    except Exception:
        return False


def delete_url(hashed_url: str) -> bool:
    try:
        redis_client = redis_connect()
        redis_client.delete(hashed_url)
        redis_client.save()
        return True
    except Exception:
        return False


def get_original_url(hashed_url: str) -> Union[str, None]:
    try:
        redis_client = redis_connect()
        # Converting Byte to String
        original_url = str(redis_client.get(hashed_url), 'utf-8')
        return original_url
    except Exception:
        return None
