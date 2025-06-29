"""
Пакет `models` — все Pydantic-схемы, которые возвращает или принимает бэкенд.

Импортируйте модели так:
    from models import ClientModel, ServiceModel
"""

from .client import ClientModel
from .address import AddressModel
from .appointment import AppointmentModel
from .place_type import PlaceTypeModel
from .promotion import PromotionModel
from .referral import ReferralsModel
from .service import ServiceModel

__all__: list[str] = [
    "ClientModel",
    "AddressModel",
    "AppointmentModel",
    "PlaceTypeModel",
    "PromotionModel",
    "ReferralsModel",
    "ServiceModel",
]
