from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field("Travel Ready Service")
    mongodb_uri: str = Field("mongodb://localhost:27017")
    mongodb_db: str = Field("travelready")

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
