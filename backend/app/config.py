from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://postgres:password@localhost:5432/women_security_db"
    jwt_secret_key: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    dev_otp_mode: bool = True
    upload_dir: str = "uploads"
    cors_origins: str = "http://localhost:5173"

settings = Settings()
BASE_DIR = Path(__file__).resolve().parents[1]
