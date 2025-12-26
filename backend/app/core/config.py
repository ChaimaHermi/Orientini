import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "orientini_db_test")

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "DEFAULT_JWT_SECRET_KEY_ayet_chaima")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", 60 * 24))
    JWT_EXPIRATION_REMEMBER_DAYS: int = int(os.getenv("JWT_EXPIRATION_REMEMBER_DAYS", 30))

    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:4200")

    # Mail
    MAIL: str | None = os.getenv("MAIL")
    MAIL_PASSWORD: str | None = os.getenv("PASSWORD")

    # Google OAuth
    GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str | None = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str | None = os.getenv("GOOGLE_REDIRECT_URI")


settings = Settings()
