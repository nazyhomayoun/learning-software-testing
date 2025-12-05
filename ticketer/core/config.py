"""Application configuration using pydantic-settings."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ticketing"
    TEST_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5433/ticketing_test"

    # Security
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    PROJECT_NAME: str = "Ticketer"
    API_V1_STR: str = "/api/v1"

    # Hold expiration (in minutes)
    HOLD_EXPIRATION_MINUTES: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()
