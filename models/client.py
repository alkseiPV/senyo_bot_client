# models/client.py

from typing import List, Optional
from pydantic import BaseModel, Field
from models.address import AddressModel  # предполагается, что вы создадите models/address.py

class ClientModel(BaseModel):
    id: int
    name: Optional[str] = Field(default='Без имени')
    surname: Optional[str] = Field(default='')
    phone: Optional[str] = Field(default='')
    gender: Optional[str] = Field(default='')
    permanent_points: float = Field(..., alias='permanent_points')
    temporary_points: float = Field(..., alias='temporary_point')
    telegram_id: int = Field(..., alias='telegram_id')
    addresses: List[AddressModel]

    class Config:
        allow_population_by_field_name = True
        # разрешаем инициализировать через alias-ы ("permanent_points", "temporary_point", "telegram_id")
