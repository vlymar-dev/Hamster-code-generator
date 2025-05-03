from pydantic import BaseModel, ConfigDict


class AnnouncementCreateSchema(BaseModel):
    title: str
    image_url: str | None = None
    created_by: int


class AnnouncementTranslationTextSchema(BaseModel):
    text: str


class AnnouncementTranslationCreateSchema(BaseModel):
    announcement_id: int
    text: AnnouncementTranslationTextSchema
    language_code: str


class AnnouncementTranslationSchema(BaseModel):
    id: int | None = None
    language_code: str | None = None
    text: str | None = None


class AnnouncementWithLanguagesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    languages: list[AnnouncementTranslationSchema]
    image_url: str | None = None
