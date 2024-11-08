import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class DbConfig:
    host: str
    port: str
    password: str
    user: str
    database: str

    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.user}:{self.password}@:{self.port}/{self.database}'


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig


def load_config(path: str = None) -> Config:
    load_dotenv(path)
    return Config(
        tg_bot=TgBot(
            token=os.getenv('BOT_TOKEN', 'token'),
        ),
        db=DbConfig(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', 5432),
            password=os.getenv('POSTGRES_PASSWORD', 'password'),
            user=os.getenv('POSTGRES_USER', 'user'),
            database=os.getenv('POSTGRES_DB', 'database'),
        ),
    )

config = load_config('.env.env')
