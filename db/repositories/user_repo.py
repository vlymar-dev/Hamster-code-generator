import logging

from sqlalchemy import select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bot.exceptions.exceptions import UserAlreadyExistsException
from core.shemas.user import UserCreateSchema
from infrastructure.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:

    @staticmethod
    async def add_user(session: AsyncSession, user: UserCreateSchema) -> None:
        try:
            new_instance = User(**user.model_dump())
            session.add(new_instance)
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            logger.error(f'Integrity error occurred while adding user: {e}')
            raise UserAlreadyExistsException(f'User with id {user.id} already exists.')
        except DatabaseError as e:
            await session.rollback()
            logger.error(f'Database error occurred while adding user: {e}')
            raise

    @staticmethod
    async def check_user_exists(session: AsyncSession, user_id: int) -> bool:
        return await session.get(User, user_id) is not None

    @staticmethod
    async def get_user_language(session: AsyncSession, user_id: int) -> str:
        try:
            result = await session.execute(select(User.language_code).where(User.id == user_id))
            language = result.scalar_one_or_none()
            return language if language else 'en'
        except DatabaseError as e:
            logger.error(f'Database error occurred while getting language for user_id={user_id}: {e}')
            return 'en'
