from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://courier:courier@localhost:5432/courier_dispatch"
    redis_url: str = "redis://localhost:6379/0"
    batch_window_seconds: float = 2.0
    matcher_strategy: str = "nearest"  # "nearest" or "batch"
    courier_stale_seconds: int = 300  # location older than this is ignored


settings = Settings()
