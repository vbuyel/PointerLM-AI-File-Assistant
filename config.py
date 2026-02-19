from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    model_api_key: str

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        case_sensitive=False
    )

settings = Settings()

def get_postgres_url():
    return f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

def get_model_api_key():
    return settings.model_api_key
