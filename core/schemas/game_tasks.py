from pydantic import BaseModel, ConfigDict


class GameTaskResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_name: str
    task: str
    answer: str

class GameTaskResponsePaginateSchema(BaseModel):
    tasks: list[GameTaskResponseSchema]
    page: int
    total_pages: int
