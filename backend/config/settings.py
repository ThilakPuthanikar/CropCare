from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment Configuration
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = False
    PORT: int = 8000

    # URLs
    API_BASE_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: str = ""

    # Database Configuration
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3307/cropcare_db"

    # Security & Authentication Secrets
    SECRET_KEY: str = "default-insecure-secret-key-change-in-production"
    JWT_SECRET: str = "default-insecure-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # External APIs
    WEATHERSTACK_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    CHATBOT_ID: str = ""
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Admin Credentials
    ADMIN_EMAIL: str = "admin@cropcare.com"
    ADMIN_PASSWORD: str = "Cropcareadmin@123"

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_cors_origins(self) -> List[str]:
        if self.CORS_ORIGINS:
            origins = [
                origin.strip()
                for origin in self.CORS_ORIGINS.split(",")
                if origin.strip()
            ]
            if origins:
                return origins
        if self.ENVIRONMENT.lower() == "production":
            if self.FRONTEND_URL:
                return [self.FRONTEND_URL.strip()]
            return []
        return [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]


settings = Settings()
