import functools

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQSettings(BaseSettings):
    HOST: str = Field(validation_alias="RABBIT_HOST")
    USER: str = Field(validation_alias="RABBIT_USER")
    PASSWORD: SecretStr = Field(validation_alias="RABBIT_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


class Settings(BaseSettings):
    DETECTION_BATCH_SIZE: int

    rabbitmq_settings: RabbitMQSettings = RabbitMQSettings()
    API_URL: str

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
