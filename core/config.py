from pathlib import Path
from urllib.parse import quote

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env',
                                      env_file_encoding='utf-8',
                                      extra='ignore')


class BotConfig(ConfigBase):
    model_config = {
        **ConfigBase.model_config,
        'env_prefix': 'BOT_'
    }

    TOKEN: str
    ADMIN_ACCESS_IDs: list[int]
    SUPPORT_LINK: str
    NAME: str
    DEFAULT_LANGUAGE: str = 'en'
    POPULARITY_COEFFICIENT: int = 1
    REFERRAL_THRESHOLD: int = 5

    def generate_referral_link(self, user_id: int) -> str:
        return f'https://t.me/{self.NAME}?start={user_id}'


class WalletsConfig(ConfigBase):
    model_config = {
        **ConfigBase.model_config,
        'env_prefix': 'WALLET_'
    }

    TRC: str
    TON: str


class DatabaseConfig(ConfigBase):
    model_config = {
        **ConfigBase.model_config,
        'env_prefix': 'DATABASE_'
    }

    NAME: str = 'hamster'
    USER: str = 'postgres'
    PASSWORD: str = 'postgres'
    PORT: int = 5432
    HOST: str = '0.0.0.0'
    DRIVER: str = 'postgresql+asyncpg'

    @property
    def database_url(self) -> str:
        user = quote(self.USER)
        password = quote(self.PASSWORD)
        return f'{self.DRIVER}://{user}:{password}@{self.HOST}:{self.PORT}/{self.NAME}'


class Config(BaseSettings):
    telegram: BotConfig = Field(default_factory=BotConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    wallets: WalletsConfig = Field(default_factory=WalletsConfig)


config = Config()
