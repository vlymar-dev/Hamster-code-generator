from aiogram.utils.i18n import gettext as _


def get_achievement_text(key: str) -> str:
    """
    Returns the translated text of the achievement key.

    :param key: Achievement key.
    :return: The text of the achievement in string format.
    """
    achievements = {
        'newcomer': _('🌱 <b>Newcomer</b> — <i>You\'ve just begun your journey! Keep going, there are many opportunities ahead!</i> 🚀'),
        'adventurer': _('🔑 <b>Adventurer</b> — <i>You\'ve unlocked a few doors, but more valuable keys await you.</i> 💎'),
        'bonus_hunter': _('🎯 <b>Bonus Hunter</b> — <i>With each new key, you grow stronger. Unlock bonuses!</i> 🎁'),
        'code_expert': _('🧠 <b>Code Expert</b> — <i>You already know how the system works. Keep improving!</i> 📈'),
        'game_legend': _('🌟 <b>Game Legend</b> — <i>You\'ve achieved almost everything! Stay at the top and collect all the keys!</i> 🏅'),
        'absolute_leader': _('👑 <b>Absolute Leader</b> — <i>You\'re at the top! All the keys are at your disposal, and you\'re a role model for everyone!</i> 🌍')
    }
    return achievements.get(key, achievements['newcomer'])

def get_status_text(key: str) -> str:
    """
    Returns the translated status text by key.

    :param key: Status key.
    :return: Status text in string format.
    """
    statuses = {
        'free': _('🎮 <b>Regular Player</b> — Get keys and open doors to become stronger. 🚀'),
        'friend': _('🤝 <b>Friend of the Project</b> — You have access to exclusive features, but there\'s more ahead! 🔥'),
        'premium': _('👑 <b>Elite Player!</b> Use all your privileges and enjoy exclusive content. ✨')
    }
    return statuses.get(key, statuses['free'])