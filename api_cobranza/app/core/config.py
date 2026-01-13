from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Stripe keys
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_ENDPOINT_SECRET: str

    # URLs
    STRIPE_SUCCESS_URL: str
    STRIPE_CANCEL_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
