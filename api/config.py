from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/app.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    S3_ENDPOINT: str = ""
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    E_CHALLAN_URL: str = ""

settings = Settings()
