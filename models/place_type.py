from typing import Optional

from pydantic import BaseModel, Field

class PlaceTypeModel(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    class Config:
        allow_population_by_field_name = True
