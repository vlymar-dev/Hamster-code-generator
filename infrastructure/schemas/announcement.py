from pydantic import BaseModel, ConfigDict


class AnnouncementCreateSchema(BaseModel):
    title: str
    image_url: str | None = None
    created_by: int


class AnnouncementTranslationCreateSchema(BaseModel):
    announcement_id: int
    text: str
    language_code: str


class AnnouncementTranslationSchema(BaseModel):
    language_code: str | None = None
    text: str | None = None


class AnnouncementWithLanguagesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    languages: list[AnnouncementTranslationSchema]
    image_url: str | None = None
