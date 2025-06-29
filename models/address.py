# models/address.py

from typing import Optional
from pydantic import BaseModel, Field

class AddressModel(BaseModel):
    id: int
    address: str
    status: Optional[str] = None
    id_client: int = Field(..., alias='id_client')

    class Config:
        allow_population_by_field_name = True
