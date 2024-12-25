from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.logger_config import logger

BASE_DIR = Path(__file__).parent.parent


class DBConfig(BaseSettings):
    driver: str
    host: str
    port: int | None = Field(default=None)
    username: str
    password: str
    database: str = Field(validation_alias='db_name')

    @property
    def db_url(self):
        url = f"{self.driver}://{self.username}:{self.password}@{self.host}{f':{self.port}' if self.port else ''}/{self.database}"
        logger.debug(f"db_url: {url}")
        return url

    model_config = SettingsConfigDict(env_prefix="DB_",
                                      env_file=Path(__file__).parents[3] / ".conf" / ".env",
                                      extra="allow")


class Settings(BaseSettings):
    secret: str = "some text"
    private_key_path: Path = BASE_DIR / "api_v1" / "user" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "api_v1" / "user" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 120
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    CREATE_REDIRECT_URL: str = "http://localhost:8000"


class S3Config(BaseSettings):
    username: str = Field(validation_alias='s3_local_username')
    password: str = Field(validation_alias='s3_local_password')
    access_key: str
    secret_key: str
    uri: str

    model_config = SettingsConfigDict(env_prefix='S3_',
                                      env_file=Path(__file__).parents[3] / ".conf" / ".env",
                                      extra="allow")


logger.debug(f"Path to environment file: {Path(__file__).parents[3] / '.conf' / '.env'}")
SETTINGS_CONFIG = Settings()
db_config = DBConfig()
s3_config = S3Config()
