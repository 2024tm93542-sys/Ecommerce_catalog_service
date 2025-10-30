from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str
    MYSQL_DB: str = "ecommerce"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
