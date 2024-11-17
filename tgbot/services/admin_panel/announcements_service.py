from infrastructure.models.announcement_model import Announcement
from infrastructure.repositories.announcement_repo import AnnouncementRepository


class AnnouncementService:

    @staticmethod
    async def show_announcements( announcement_repo: AnnouncementRepository) -> list[Announcement]:
        announcements = await announcement_repo.get_all_announcements()
        return announcements


    @staticmethod
    async def create_announcement(title: str, text: str, created_by: int, announcement_repo: AnnouncementRepository,
                                  image_url: str = None,) -> Announcement:
        new_announcement = Announcement(
            title=title,
            text=text,
            image_url=image_url,
            created_by=created_by
        )
        await announcement_repo.add_announcement(new_announcement)
        return new_announcement
