from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_HOST: str = Field(default='localhost')
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DATABASE: str = Field(default='ecom')
    POSTGRES_USER: str = Field(default='postgres')
    POSTGRES_PASSWORD: str = Field(default='1')

    # JWT
    JWT_SECRET_KEY: str = Field(default='secret')
    JWT_ALGORITHM: str = Field(default='HS256')
    JWT_ACCESS_TOKEN_EXPIRE_TIME: int = Field(default=60)
    JWT_REFRESH_TOKEN_EXPIRE_TIME: int = Field(default=10080)

    SECRET_KEY: str = Field(default='secret_key')
    ADMIN_BOOTSTRAP_KEY: str = Field(default='change-me')

    # redis
    REDIS_URL: str = Field(default='redis://localhost:6379/1')
    OTP_EXPIRE_SECONDS: int = Field(default=300)
    OTP_RESEND_SECONDS: int = Field(default=60)
    OTP_MAX_ATTEMPTS: int = Field(default=5)
    REGISTRATION_DATA_EXPIRE_SECONDS: int = Field(default=300)
    PASSWORD_RESET_DATA_EXPIRE_SECONDS: int = Field(default=300)

    @property
    def postgres_sync_url(self):
        return (f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")

    @property
    def postgres_async_url(self):
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")

    class Config:
        env_file = '.env'


settings = Settings()
