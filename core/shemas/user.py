from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    language_code: str
