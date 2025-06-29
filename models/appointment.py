# models/appointment.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class AppointmentModel(BaseModel):
    id: int
    place: str
    status: str
    date: datetime
    client_name: str = Field(..., alias='client_name')
    client_phone: str = Field(..., alias='client_phone')
    client_gender: str = Field(..., alias='client_gender')
    client_points: float = Field(..., alias='client_points')
    service_price: float = Field(..., alias='service_price')
    service_name: str = Field(..., alias='service_name')
    final_sum: float = Field(..., alias='final_sum')
    used_points: Optional[float] = Field(None, alias='used_points')

    class Config:
        allow_population_by_field_name = True
