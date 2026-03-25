from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "my-mcp-server"
    transport: str = "stdio"          # "stdio" | "sse"
    host: str = "0.0.0.0"
    port: int = 3000
    log_level: str = "INFO"
    api_key: str                       # Required — fails at startup if missing
    database_url: str = ""
    redis_url: str = "redis://localhost:6379"
    rate_limit_per_minute: int = 100

    @field_validator("api_key")
    @classmethod
    def key_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("API key must be at least 32 characters")
        return v


settings = Settings()