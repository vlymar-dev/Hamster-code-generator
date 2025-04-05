from pydantic import BaseModel, ConfigDict


class GameTaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_name: str
    task: str
    answer: str

class GameTaskResponsePaginateSchema(BaseModel):
    tasks: list[GameTaskSchema]
    page: int
    total_pages: int
