from pydantic import BaseSettings

from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str
    items_per_user: int = 50

    class Config:
        env_file = ".env"

#
# settings = Settings()
#
#
# @lru_cache()
# def get_settings():
#     return Settings()
