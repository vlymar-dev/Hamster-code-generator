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

    async def get_user_language(self, user_id: int) -> str:
        user = await self.session.get(User, user_id)
        if user:
            return user.language_code
        return None

    async def update_user_language(self, user_id: int, selected_language_code: str) -> None:
        user = await self.session.get(User, user_id)
        if user:
            if user.language_code != selected_language_code:
                user.language_code = selected_language_code
                await self.session.commit()
