from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Incident Decision Engine"


settings = Settings()

