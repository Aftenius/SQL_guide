"""Process settings loaded from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration.

    Attributes:
        app_name: Title shown by the API.
        database_url: Async connection string for the application database.
        jwt_secret: HMAC secret for access tokens.
        access_token_ttl_minutes: Lifetime of an access token.
        refresh_token_ttl_days: Lifetime of a refresh token.
        cookie_secure: Whether the refresh cookie requires HTTPS.
        password_hash_rounds: bcrypt cost used for new passwords.
        yandex_client_id: Yandex OAuth client id.
        yandex_client_secret: Yandex OAuth client secret.
        yandex_redirect_uri: Callback URL registered in Yandex.
        frontend_origin: Browser origin allowed to call the API.
        sandbox_database_url: Database where learner SQL is executed.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "SQL Guide"
    database_url: str = (
        "postgresql+psycopg://sql_guide:sql_guide@127.0.0.1:5433/sql_guide"
    )
    jwt_secret: str = "dev-only-change-me"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 14
    cookie_secure: bool = False
    password_hash_rounds: int = 12
    yandex_client_id: str = ""
    yandex_client_secret: str = ""
    yandex_redirect_uri: str = "http://127.0.0.1:5173/login/yandex"
    frontend_origin: str = "http://127.0.0.1:5173"
    sandbox_database_url: str = (
        "postgresql://sql_guide:sql_guide@127.0.0.1:5433/sql_guide_sandbox"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once per process.

    Returns:
        The cached settings instance.
    """
    return Settings()
