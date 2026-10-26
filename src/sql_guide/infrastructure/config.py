"""Process settings loaded from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration.

    Attributes:
        app_name: Title shown by the API.
        database_url: Connection string for the application database.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "SQL Guide"
    database_url: str = "postgresql://sql_guide:sql_guide@localhost:5432/sql_guide"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once per process.

    Returns:
        The cached settings instance.
    """
    return Settings()
