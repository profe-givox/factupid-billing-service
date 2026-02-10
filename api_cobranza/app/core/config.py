from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Stripe keys
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_ENDPOINT_SECRET: str

    # URLs
    STRIPE_SUCCESS_URL: str
    STRIPE_CANCEL_URL: str


    # Main app webhook (Django)
    MAIN_APP_BASE: str = "http://127.0.0.1:8000"
    MAIN_APP_WEBHOOK_SECRET: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()


