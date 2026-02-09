from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Stripe keys
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_ENDPOINT_SECRET: str

    # URLs
    STRIPE_SUCCESS_URL: str
    STRIPE_CANCEL_URL: str

<<<<<<< HEAD
    # Main app webhook (Django)
    MAIN_APP_BASE: str = "http://127.0.0.1:8000"
    MAIN_APP_WEBHOOK_SECRET: str = ""

=======
>>>>>>> imanol
    class Config:
        env_file = ".env"


settings = Settings()
