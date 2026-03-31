from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Stripe keys
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_ENDPOINT_SECRET: str

    # URLs
    STRIPE_SUCCESS_URL: str
    STRIPE_CANCEL_URL: str
    
    # Database
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
