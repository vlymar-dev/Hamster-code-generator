import os
import random
from datetime import date, datetime
from typing import Optional

from aiogram import Bot
from aiogram.types import FSInputFile

from tgbot.config import config


def get_current_time() -> datetime:
    return datetime.now()


def get_current_date() -> date:
    return datetime.now().date()


def format_seconds_to_minutes_and_seconds(seconds: int) -> dict[str, Optional[int]]:
    minutes = seconds // 60
    seconds = seconds % 60
    return {'min': minutes if minutes > 0 else None, 'sec': seconds}


class ImageCacheManager:
    """Управляет кэшем file_id для изображений."""

    def __init__(self):
        self._cache = {}

    def get_random_cached_file_id(self) -> str | None:
        """Возвращает случайный file_id из кэша, если он есть."""
        if self._cache:
            file_id = random.choice(list(self._cache.values()))
            print(f"Выбран из кэша: {file_id}")
            return file_id
        print("Кэш пуст.")
        return None

    def add_to_cache(self, file_path: str, file_id: str) -> None:
        """Добавляет file_id в кэш, ассоциируя его с локальным путем."""
        if file_path not in self._cache:
            self._cache[file_path] = file_id
            print(f"Добавлено в кэш: {file_path} -> {file_id}")
        else:
            print(f"Уже в кэше: {file_path} -> {file_id}")

    def remove_from_cache(self, file_id: str) -> None:
        """Удаляет file_id из кэша."""
        for key, value in list(self._cache.items()):
            if value == file_id:
                print(f"Удаляю из кэша: {key} -> {file_id}")
                del self._cache[key]
                break

    def is_file_in_cache(self, file_path: str) -> bool:
        """Проверяет, есть ли файл в кэше."""
        return file_path in self._cache


async def is_file_id_available(bot: Bot, file_id: str) -> bool:
    """Проверяет, доступен ли file_id на серверах Telegram."""
    try:
        await bot.get_file(file_id)
        return True
    except Exception:
        return False


async def get_new_file_id(bot: Bot, folder_path: str, cache_manager: ImageCacheManager) -> tuple[str | None, str | None]:
    """
    Загружает случайное изображение из локальной папки и возвращает новый file_id.
    Возвращает (file_id, file_path) или (None, None), если изображения нет.
    """
    if not os.path.exists(folder_path):
        print(f"Папка {folder_path} не существует.")
        return None, None

    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'webp'))]
    if not images:
        print("В папке нет изображений.")
        return None, None

    # Убираем из списка файлы, которые уже в кэше
    uncached_images = [img for img in images if not cache_manager.is_file_in_cache(os.path.join(folder_path, img))]

    # Если все файлы в кэше, выбираем случайный из кэша
    if not uncached_images:
        print("Все файлы уже в кэше.")
        return cache_manager.get_random_cached_file_id(), None

    random_image_path = os.path.join(folder_path, random.choice(uncached_images))

    # Конвертируем .webp в .png, если нужно
    converted_image_path = convert_webp_to_png(random_image_path)

    try:
        # Используем FSInputFile для отправки файла
        file_to_send = FSInputFile(converted_image_path)

        sent_message = await bot.send_photo(
            chat_id=config.tg_bot.bot_info.admin_chat_id,
            photo=file_to_send
        )
        file_id = sent_message.photo[-1].file_id
        print(f"Загружено изображение {converted_image_path} -> {file_id}")
        return file_id, converted_image_path
    except Exception as e:
        print(f"Ошибка при загрузке изображения {converted_image_path}: {e}")
        return None, None



async def get_random_image(bot: Bot, cache_manager: ImageCacheManager, folder_path: str) -> str | FSInputFile | None:
    """
    Возвращает случайное изображение.
    1. Если file_id из кэша доступен, возвращаем его.
    2. Если нет, загружаем новое изображение из папки.
    """
    # Попытка использовать file_id из кэша
    cached_file_id = cache_manager.get_random_cached_file_id()
    if cached_file_id and await is_file_id_available(bot, cached_file_id):
        return cached_file_id
    elif cached_file_id:
        # Если file_id больше не доступен, удаляем его из кэша
        cache_manager.remove_from_cache(cached_file_id)

    # Попытка загрузить новое изображение из папки
    new_file_id, image_path = await get_new_file_id(bot, folder_path)
    if new_file_id:
        cache_manager.add_to_cache(image_path, new_file_id)
        return new_file_id

    # Если ничего не найдено, возвращаем None
    return None
