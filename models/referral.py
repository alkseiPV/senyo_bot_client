# models/referrals.py

from pydantic import BaseModel, Field

class ReferralsModel(BaseModel):
    id: int
    id_client: int = Field(..., alias='id_client')
    referral_phone: str = Field(..., alias='refferal_phone')
    is_active: bool = Field(..., alias='is_active')

    class Config:
        allow_population_by_field_name = True
