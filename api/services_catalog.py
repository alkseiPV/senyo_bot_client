from typing import List

from models.service import ServiceModel
from .base import base_api


async def get_services_list() -> List[ServiceModel]:
    data = await base_api.get("/services")
    return [ServiceModel(**item) for item in data]
