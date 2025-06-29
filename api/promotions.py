from typing import List

from models.promotion import PromotionModel
from .base import base_api


async def get_promotions() -> List[PromotionModel]:
    data = await base_api.get("/promotions")
    return [PromotionModel(**item) for item in data]
