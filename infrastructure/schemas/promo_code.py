from pydantic import BaseModel, ConfigDict


class PromoCodeCreateSchema(BaseModel):
    game_name: str
    promo_code: str


class PromoCodeReceiveSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_name: str
    promo_code: str | None
