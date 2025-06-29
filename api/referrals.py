from typing import List, Optional

from models.referral import ReferralsModel
from .base import base_api


async def get_referrals(client_id: int) -> List[ReferralsModel]:
    data = await base_api.get(f"/referrals/{client_id}")
    return [ReferralsModel(**item) for item in data]


async def create_referral(client_id: int, referral_phone: str, *, is_active: bool = True) -> ReferralsModel:
    payload = {
        "id_client": client_id,
        "referral_phone": referral_phone,
        "is_active": is_active,
    }
    data = await base_api.post("/referrals", json=payload)
    return ReferralsModel(**data)


async def update_referral(
    referral_id: int,
    *,
    is_active: Optional[bool] = None,
    referral_phone: Optional[str] = None,
) -> ReferralsModel:
    payload: dict[str, object] = {"id": referral_id}
    if is_active is not None:
        payload["is_active"] = is_active
    if referral_phone is not None:
        payload["referral_phone"] = referral_phone
    data = await base_api.put("/referrals", json=payload)
    return ReferralsModel(**data)


async def delete_referral(referral_id: int) -> None:
    await base_api.delete(f"/referrals?id={referral_id}")
