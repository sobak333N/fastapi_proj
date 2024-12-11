from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_EXP_MINUTES: int
    JWT_REFRESH_EXP_DAYS: int
    
    EMAIL_TOKENS_EX_MINUTES: int

    PAGE_LIMIT: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_INNER_PORT: int

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str    
    REDIS_INNER_PORT: int

    @property
    def DATABASE_URL(self) -> str:
        # postgresql+asyncpg://postgres:postgres@db/postgres
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        extra = "ignore"



Config = Settings()


broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True