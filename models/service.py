# models/service.py

from pydantic import BaseModel

class ServiceModel(BaseModel):
    id: int
    title: str
    duration: str
    subtitle: str
    price: int
