from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "BBP API Gateway"
    PORT: int = 8080

    JWT_SECRET_KEY: str = "23qecb" #just a random fallback key
    JWT_ALGORITHM: str = "HS256"

    USER_SERVICE_URL: str
    TRIP_SERVICE_URL: str
    PATH_SERVICE_URL: str

    RATE_LIMIT_PER_MINUTE: int = 60

    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_TIMEOUT: int = 60

    SERVICE_REQUEST_TIMEOUT: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
