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
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}'

@dataclass
class BotInfo:
    username: str
    support_link: str

    def generate_referral_link(self, user_id: int) -> str:
        return f'https://t.me/{self.username}?start={user_id}'


@dataclass
class Wallets:
    trc_wallet: str
    ton_wallet: str

@dataclass
class BotSettings:
    admin_id: int
    referral_threshold: int


@dataclass
class TgBot:
    token: str
    bot_info: BotInfo
    wallets: Wallets
    bot_settings: BotSettings


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig


def load_config(path: str = None) -> Config:
    load_dotenv(path)
    return Config(
        tg_bot=TgBot(
            token=os.getenv('BOT_TOKEN', 'token'),
            bot_info=BotInfo(
                username=os.getenv('BOT_USERNAME', 'bot_username'),
                support_link=os.getenv('SUPPORT_LINK', 'support_link'),
            ),
            wallets=Wallets(
                trc_wallet=os.getenv('TRC_WALLET', 'wallet_address'),
                ton_wallet=os.getenv('TON_WALLET', 'wallet_address')
            ),
            bot_settings=BotSettings(
                admin_id=int(os.getenv('ADMIN_ACCESS_ID', '')),
                referral_threshold=int(os.getenv('REFERRAL_THRESHOLD', 10)),
            )
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
