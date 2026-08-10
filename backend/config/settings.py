from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000"
    WEATHERSTACK_API_KEY: str
    GROQ_API_KEY: str
    CHATBOT_ID: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    
    class Config:
        env_file = ".env"

settings = Settings()
