from typing import List, Optional

from models.place_type import PlaceTypeModel
from .base import base_api


async def get_place_types() -> List[PlaceTypeModel]:
    data = await base_api.get("/place-type")
    return [PlaceTypeModel(**item) for item in data]


async def create_place_type(title: str, description: Optional[str] = None) -> PlaceTypeModel:
    payload = {"title": title}
    if description is not None:
        payload["description"] = description
    data = await base_api.post("/place-type", json=payload)
    return PlaceTypeModel(**data)


async def update_place_type(
    place_type_id: int,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> PlaceTypeModel:
    payload: dict[str, object] = {"id": place_type_id}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    data = await base_api.put("/place-type", json=payload)
    return PlaceTypeModel(**data)


async def delete_place_type(place_type_id: int) -> None:
    await base_api.delete(f"/place-type?id={place_type_id}")
