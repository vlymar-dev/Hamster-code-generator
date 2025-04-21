import logging
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.models.base import Base

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=Base)


class BaseDAO(Generic[T]):
    """Base DAO (Data Access Object) for interacting with SQLAlchemy models."""

    model: type[T]

    @classmethod
    async def add(cls, session: AsyncSession, values: BaseModel):
        """Adds a new record to the database.

        Args:
            session (AsyncSession): The database session.
            values (BaseModel): The data for the new record.

        Returns:
            T: The newly created record.
        """
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f'Adding a record {cls.model.__name__} with parameters: {values_dict}')
        new_instance = cls.model(**values_dict)
        session.add(new_instance)
        try:
            await session.flush()
            logger.info(f'Record {cls.model.__name__} has been successfully added.')
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Error when adding a record: {e}')
            raise e
        return new_instance

    @classmethod
    async def find_one_or_none_by_id(cls, session: AsyncSession, data_id: int):
        """Finds a record by its ID.

        Args:
            session (AsyncSession): The database session.
            data_id (int): The record ID.

        Returns:
            T | None: The record if found, otherwise None.
        """
        logger.info(f'Searching for {cls.model.__name__} with ID: {data_id}')
        try:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f'Error while searching for record with ID {data_id}: {e}')
            raise

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: BaseModel):
        """Finds a single record by filters.

        Args:
            session (AsyncSession): The database session.
            filters (BaseModel): Filtering conditions.

        Returns:
            T | None: The record if found, otherwise None.
        """
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f'Searching for a record in {cls.model.__name__} with filters: {filter_dict}')
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f'Error while searching for a record with filters {filter_dict}: {e}')
            raise

    @classmethod
    async def find_field_by_id(cls, session: AsyncSession, data_id: int, field: str):
        """Finds a specific field value by record ID.

        Args:
            session (AsyncSession): The database session.
            data_id (int): The record ID.
            field (str): The field name to retrieve.

        Returns:
            Any | None: The field value if found, otherwise None.
        """
        logger.info(f'Searching for field "{field}" in {cls.model.__name__} with ID: {data_id}')
        try:
            if not hasattr(cls.model, field):
                raise AttributeError(f'Field "{field}" does not exist in {cls.model.__name__}')

            query = select(getattr(cls.model, field)).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f'Error retrieving field "{field}" for ID {data_id}: {e}')
            raise

    @classmethod
    async def count(cls, session: AsyncSession, filters: BaseModel | None = None):
        """Counts records based on filters.

        Args:
            session (AsyncSession): The database session.
            filters (BaseModel, optional): Filtering conditions.

        Returns:
            int: The count of matching records.
        """
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(f'Counting records in {cls.model.__name__} with filters: {filter_dict}')
        try:
            query = select(func.count(cls.model.id)).filter_by(**filter_dict)
            result = await session.execute(query)
            count = result.scalar()
            logger.info(f'Found {count} records.')
            return count
        except SQLAlchemyError as e:
            logger.error(f'Error counting records: {e}')
            raise

    @classmethod
    async def count_where(
        cls,
        session: AsyncSession,
        *where_conditions,
    ) -> int:
        """Counts records based on WHERE conditions (not just filter_by)."""
        try:
            query = select(func.count(cls.model.id)).where(*where_conditions)
            result = await session.execute(query)
            count = result.scalar_one_or_none()
            return count if count is not None else 0
        except SQLAlchemyError as e:
            logger.error(f'Error counting records with WHERE: {e}')
            raise

    @classmethod
    async def update(cls, session: AsyncSession, data_id: int, values: BaseModel):
        """Updates records based on filters.

        Args:
            session (AsyncSession): The database session.
            data_id (int): The record ID.
            values (BaseModel): Data to update.

        Returns:
            int: The number of updated records.
        """
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f'Updating {cls.model.__name__} with ID={data_id} and values={values_dict}')
        query = (
            update(cls.model)
            .where(cls.model.id == data_id)
            .values(**values_dict)
            .execution_options(synchronize_session='fetch')
        )
        try:
            result = await session.execute(query)
            await session.flush()
            logger.info(f'Updated {result.rowcount} record(s).')
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Error updating record with ID={data_id}: {e}')
            raise

    @classmethod
    async def delete(cls, session: AsyncSession, data_id: int):
        """Deletes records based on filters.

        Args:
            session (AsyncSession): The database session.
            data_id (int): The record ID.

        Returns:
            int: The number of deleted records.
        """

        logger.info(f'Deleting records from {cls.model.__name__} with id: {data_id}')
        query = delete(cls.model).where(cls.model.id == data_id)
        try:
            result = await session.execute(query)
            await session.flush()
            logger.info(f'Deleted {result.rowcount} records.')
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f'Error deleting records: {e}')
            raise e
