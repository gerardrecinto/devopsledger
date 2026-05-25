from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://devopsledger:devopsledger@localhost:5432/devopsledger"
    redis_url: str = "redis://localhost:6379"
    enable_docs: bool = True
    log_level: str = "info"
    environment: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
