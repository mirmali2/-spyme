from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "SPYME"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite+aiosqlite:///./spyme_dev.db"
    REDIS_URL: str = "redis://localhost:6379"

    JWT_SECRET: str = "dev-secret-change-in-production-please-use-256-bit-random"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "spyme-clips"
    S3_ENDPOINT_URL: str = ""  # set for Cloudflare R2

    FIREBASE_CREDENTIALS_PATH: str = ""

    # Twilio (for fire/emergency SMS)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""

    # Google OAuth + Drive
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_IOS_CLIENT_ID: str = ""
    GOOGLE_ANDROID_CLIENT_ID: str = ""

    # Stripe (subscriptions)
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_MONTHLY: str = ""    # price_xxx for $5/mo
    STRIPE_PRICE_YEARLY: str = ""     # price_xxx for $50/yr

    STUN_URLS: list[str] = ["stun:stun.cloudflare.com:3478", "stun:stun.l.google.com:19302"]
    TURN_URL: str = ""
    TURN_USERNAME: str = ""
    TURN_CREDENTIAL: str = ""

    CLIP_PRESIGN_EXPIRE_SECONDS: int = 3600
    UPLOAD_PRESIGN_EXPIRE_SECONDS: int = 900

    class Config:
        env_file = ".env"


settings = Settings()
