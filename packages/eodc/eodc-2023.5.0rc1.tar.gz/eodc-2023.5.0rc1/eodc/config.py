from pydantic import BaseSettings


class Settings(BaseSettings):
    ARGO_WORKFLOWS_URL: str = None


settings = Settings()
