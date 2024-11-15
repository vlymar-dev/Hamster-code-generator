from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tgbot.config import config

DATABASE_URL = config.db.db_url

# Создание движка для работы с базой данных
engine = create_async_engine(
    url=DATABASE_URL,
    echo=False,
    pool_size=3,
    max_overflow=5
)

# Фабрика для создания сессий
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
