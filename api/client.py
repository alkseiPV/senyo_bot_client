from typing import Optional

from models import ClientModel
from .base import base_api


async def register_client(telegram_id: int) -> None:
    await base_api.post("/client", json={"telegram_id": telegram_id})


async def get_client_info(client_id: int, *, is_telegram: bool = False) -> ClientModel:
    path = (
        f"/client/telegram/{client_id}"
        if is_telegram else
        f"/client/{client_id}"
    )
    data = await base_api.get(path)
    return ClientModel(**data)


async def update_client(
    *,
    id: int,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    phone: Optional[str] = None,
    gender: Optional[int] = None,
) -> None:
    payload: dict[str, object] = {"id": id}
    if name is not None:
        payload["name"] = name
    if surname is not None:
        payload["surname"] = surname
    if phone is not None:
        payload["phone"] = phone
    if gender is not None:
        payload["id_gender"] = gender
    await base_api.put("/client", json=payload)
