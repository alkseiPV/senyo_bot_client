# models/promotion.py

from datetime import datetime
from pydantic import BaseModel, Field

class PromotionModel(BaseModel):
    id: int
    title: str
    description: str
    added_points: int = Field(..., alias='added_points')
    gender: str
    start_date: datetime = Field(..., alias='start_date')
    expiration_date: datetime = Field(..., alias='expiration_date')

    class Config:
        allow_population_by_field_name = True
        # автоматически парсить даты из строк
