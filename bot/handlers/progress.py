from dataclasses import dataclass

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters import IsBannedFilter
from bot.keyboards.progress_kb import get_progress_keyboard
from core.services import progres_service

progress_router = Router()


@progress_router.callback_query(IsBannedFilter(), F.data == 'user_progress')
async def user_progress_handler(callback_query: CallbackQuery, session: AsyncSession) -> None:
    user_progress = await progres_service.get_user_progres(session=session, user_id=callback_query.from_user.id)

    if not user_progress:
        await callback_query.answer(text=_('User data not found.'), show_alert=True)
        return

    progress_text = ProgresText(achievement_key=user_progress.current_level, status_key=user_progress.user_status)
    keys_progress = progress_text.format_progress(user_progress.keys_progress, user_progress.next_level)
    referrals_progress = progress_text.format_progress(user_progress.referrals_progress, user_progress.next_level)
    days_progress = progress_text.format_progress(user_progress.days_progress, user_progress.next_level)

    text = _(
        '🏆 <b>Progress:</b>\n\n'
        '{achievement_name}\n\n'
        '🔝 <b>To the next level:</b>\n'
        '🔑 <i>Keys:</i> {keys_progress}\n'
        '📨 <i>Referrals:</i> {referrals_progress}\n'
        '⏳ <i>Days in Bot:</i> {days_progress}\n\n'
        '🥇 <b>Your status:</b>\n'
        '{user_status}\n\n'
        '🎳 Invite friends, earn keys, and reach new heights with us! 🌍'
    ).format(
        achievement_name=progress_text.get_achievement_text(),
        keys_progress=keys_progress,
        referrals_progress=referrals_progress,
        days_progress=days_progress,
        user_status=progress_text.get_status_text(),
    )
    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        text=text,
        reply_markup=get_progress_keyboard(user_id=callback_query.from_user.id)
    )


@dataclass
class ProgresText:
    achievement_key: str
    status_key: str

    def get_achievement_text(self) -> str:
        """Returns the translated text of the achievement key."""
        achievements = {
            'newcomer': _(
                '🌱 <b>Level:</b>\n<i>Newcomer</i> — <i>You\'ve just begun your journey! '
                'Keep going, there are many opportunities ahead!</i> 🚀'),
            'adventurer': _(
                '🎩 <b>Level:</b>\n<i>Adventurer</i> — <i>You\'ve unlocked a few doors, but more valuable keys await you.</i> 💎'),
            'bonus_hunter': _(
                '🎯 <b>Level:</b>\n<i>Bonus Hunter</i> — <i>With each new key, you grow stronger. Unlock bonuses!</i> 🎁'),
            'code_expert': _(
                '🧠 <b>Level:</b>\n<i>Code Expert</i> — <i>You already know how the system works. Keep improving!</i> 📈'),
            'game_legend': _(
                '🌟 <b>Level:</b>\n<i>Game Legend</i> — <i>You\'ve achieved almost everything! Stay at the top and collect all the keys!</i> 🏅'),
            'absolute_leader': _(
                '👑 <b>Level:</b>\n<i>Absolute Leader</i> — <i>You\'re at the top! All the keys are at your disposal, and you\'re a role model for everyone!</i> 🌍')
        }
        return achievements.get(self.achievement_key, achievements['newcomer'])


    def get_status_text(self) -> str:
        """Returns the translated status text by key."""
        statuses = {
            'free': _('🎮 <b>Regular Player</b> — Get keys and open doors to become stronger. 🚀'),
            'friend': _(
                '🤝 <b>Friend of the Project</b> — You have access to exclusive features, but there\'s more ahead! 🔥'),
            'premium': _('👑 <b>Elite Player!</b> Use all your privileges and enjoy exclusive content. ✨')
        }
        return statuses.get(self.status_key, statuses['free'])

    @staticmethod
    def format_progress(value: str, next_level: str | None) -> str:
        return value if next_level else _('Max level achieved ✔️')
