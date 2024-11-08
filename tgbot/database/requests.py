from tgbot.database.models import User

from sqlalchemy.ext.asyncio import AsyncSession

from typing import Any

class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, user_data: dict[str, Any]) -> None:
        user = await self.session.get(User, user_data["id"])
        if not user:
            user = User(**user_data)
            self.session.add(user)
        await self.session.commit()
