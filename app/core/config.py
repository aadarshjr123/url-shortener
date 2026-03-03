from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str | None = None
    BASE_URL: str = "http://localhost:8080"

    class Config:
        env_file = ".env"


settings = Settings()