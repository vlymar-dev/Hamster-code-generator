from pathlib import Path
from urllib.parse import quote

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='BOT_', env_file=BASE_DIR / '.env', env_file_encoding='utf-8', extra='ignore'
    )

    TOKEN: SecretStr
    ADMIN_ACCESS_IDs: list[int]
    SUPPORT_LINK: str
    NAME: str = Field(min_length=3, pattern=r'^[a-zA-Z0-9_]+$')
    DEFAULT_LANGUAGE: str = Field('en')
    POPULARITY_COEFFICIENT: int = Field(1)
    REFERRAL_THRESHOLD: int = Field(5)

    def generate_referral_link(self, user_id: int) -> str:
        same_name = quote(self.NAME, safe='')
        return f'https://t.me/{same_name}?start={user_id}'


class WalletsConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='WALLET_', env_file=BASE_DIR / '.env', env_file_encoding='utf-8', extra='ignore'
    )

    TRC: str
    TON: str


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='DB_', env_file=BASE_DIR / '.env', env_file_encoding='utf-8', extra='ignore'
    )

    NAME: str = Field(min_length=3)
    USER: str = Field(min_length=3)
    PASSWORD: SecretStr = Field(min_length=8)
    PORT: int = Field(5432, ge=1024, le=65535)
    HOST: str = Field('postgres')
    DRIVER: str = Field('postgresql+asyncpg')

    @property
    def database_url(self) -> str:
        user = quote(self.USER)
        password = quote(self.PASSWORD.get_secret_value())
        return f'{self.DRIVER}://{user}:{password}@{self.HOST}:{self.PORT}/{self.NAME}'


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='REDIS_', env_file=BASE_DIR / '.env', env_file_encoding='utf-8', extra='ignore'
    )

    HOST: str = Field('redis')
    PORT: int = Field(6379, ge=1024, le=65535)
    DB: int = Field(0)
    USERNAME: str | None = None
    PASSWORD: SecretStr | None = None
    TTL: int | None = Field(3600, description='Default TTL in seconds')
    FSM_TTL: int | None = Field(3600)
    DATA_TTL: int | None = Field(7200)

    @property
    def dsn(self) -> str:
        credentials = ''
        if self.PASSWORD:
            credentials += f':{quote(self.PASSWORD.get_secret_value())}'
        if self.USERNAME:
            credentials += quote(self.USERNAME)
        if credentials:
            credentials += '@'
        return f'redis://{credentials}{self.HOST}:{self.PORT}/{self.DB}'


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env', env_file_encoding='utf-8', extra='ignore')

    PROD_MODE: bool = Field(default=True, validation_alias='PRODUCTION_MODE')
    STARTUP_METHOD: int = Field(default=2)

    telegram: BotConfig = BotConfig()
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    wallets: WalletsConfig = WalletsConfig()


config = Config()
