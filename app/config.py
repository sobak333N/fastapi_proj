from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator


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
    TEST_POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_INNER_PORT: int

    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_DB: str
    MONGO_HOST: str
    MONGO_INNER_PORT: int

    S3_URL: str
    S3_BUCKET: str
    S3_ACCESS_KEY: str
    S3_SECRET_ACCESS_KEY: str
    REGION: str
    MAX_FILE_SIZE: int
    
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str    
    REDIS_INNER_PORT: int

    TESTING: str

    @property
    def DATABASE_URL(self) -> str:
        # postgresql+asyncpg://postgres:postgres@db/postgres
        if self.TESTING != "FALSE": 
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.TEST_POSTGRES_DB}"
        else:
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"

    @property
    def MONGO_DB_URL(self) -> str:
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_INNER_PORT}/{self.MONGO_DB}?authSource=admin"

    @validator("MAX_FILE_SIZE", pre=True)
    def parse_max_file_size(cls, value: str) -> int:
        if value.endswith("MB"):
            return int(value[:-2]) * 1024 * 1024 
        raise Exception(message="NOT CORRECT MAX_FILE_SIZE")
    
    class Config:
        env_file = ".env"
        extra = "ignore"



Config = Settings()


broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True