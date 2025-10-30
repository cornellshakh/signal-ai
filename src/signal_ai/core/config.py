from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Manages the application's configuration settings."""

    model_config = SettingsConfigDict(extra="ignore")

    signal_service: str = Field(..., alias="SIGNAL_SERVICE")
    signal_phone_number: str = Field(..., alias="PHONE_NUMBER")
    google_api_key: str = Field(..., alias="GEMINI_API_KEY")

    postgres_db: str = "signal_ai"
    postgres_user: str = "user"
    postgres_password: str = "password"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379

    @property
    def database_url(self) -> str:
        """Returns the full database connection URL."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        """Returns the full Redis connection URL."""
        return f"redis://{self.redis_host}:{self.redis_port}"


settings = Settings()