from typing import List, Optional
from models.appointment import AppointmentModel
from .base import base_api


async def create_appointment(
    *,
    id_client: int,
    id_address: Optional[int],
    final_sum: int,
    id_service: int,
    id_place_type: int,
    date_iso: str,
    used_points: int = 0,
    user_agent: str = "client",
) -> None:
    """
    POST /appointment
    """
    path = f"/appointment?user_agent={user_agent}"
    payload = {
        "id_client": id_client,
        "id_address": id_address,
        "date": date_iso,
        "final_sum": final_sum,
        "id_services": id_service,
        "id_place_type": id_place_type,
        "used_points": used_points,
    }
    await base_api.post(path, json=payload)


async def get_appointments(client_id: int) -> List[AppointmentModel]:
    """
    GET /appointment/{client_id}
    """
    data = await base_api.get(f"/appointment/{client_id}")
    data = [data] if isinstance(data, dict) else data
    return [AppointmentModel(**item) for item in data]


async def get_appointment_by_id(appointment_id: int) -> AppointmentModel:
    """
    GET /appointment?id={appointment_id}
    """
    data = await base_api.get(f"/appointment?id={appointment_id}")
    return AppointmentModel(**data)

async def cancel_appointment(appointment_id: int) -> None:
    """
    PUT /appointment/cancel/{appointment_id}
    """
    await base_api.put(f"/appointment/cancel/{appointment_id}")