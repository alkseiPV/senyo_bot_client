from models.address import AddressModel
from .base import base_api


async def create_address(client_id: int, address: str) -> AddressModel:
    """
    POST /address
    """
    payload = {"id_client": client_id, "address": address}
    data = await base_api.post("/address", json=payload)
    return AddressModel(**data)


async def delete_address(address_id: int) -> None:
    """
    DELETE /address?id={address_id}
    """
    await base_api.delete(f"/address?id={address_id}")
