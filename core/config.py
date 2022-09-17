from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME = 'Mini Link (Exbito)'
    PROJECT_VERSION = 1.1
    PROJECT_DESCRIPTION = "A simple but reliable URL shortener :)"

    URL_PREFIX = '/minilink'

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = 5432
    POSTGRES_DB: str
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    class Config:
        env_file = ".env"


settings = Settings()
