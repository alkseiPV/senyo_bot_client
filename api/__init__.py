"""
Удобный единый вход в API-слой.

Импортируйте нужные функции прямо отсюда, напр.:
    from api import get_client_info, create_address
"""

# ──────────────────────────────────────────
# базовый низкоуровневый клиент (одна сессия)
# ──────────────────────────────────────────
from .base import base_api       # для graceful-shutdown в main.py

# ──────────────────────────────────────────
# доменные функции, ре-экспорт
# ──────────────────────────────────────────
from .address import create_address, delete_address
from .appointment import (           # ← БЕЗ двойных точек
    create_appointment,
    get_appointments,
    get_appointment_by_id,
)
from .client import (
    register_client,
    get_client_info,
    update_client,
)
from .place_type import (
    get_place_types,
    create_place_type,
    update_place_type,
    delete_place_type,
)
from .promotions import get_promotions
from .referrals import (
    get_referrals,
    create_referral,
    update_referral,
    delete_referral,
)
from .services_catalog import get_services_list

__all__ = [
    # base
    "base_api",
    # address
    "create_address",
    "delete_address",
    # appointment
    "create_appointment",
    "get_appointments",
    "get_appointment_by_id",
    # client
    "register_client",
    "get_client_info",
    "update_client",
    # place_type
    "get_place_types",
    "create_place_type",
    "update_place_type",
    "delete_place_type",
    # promotions
    "get_promotions",
    # referrals
    "get_referrals",
    "create_referral",
    "update_referral",
    "delete_referral",
    # services
    "get_services_list",
]
