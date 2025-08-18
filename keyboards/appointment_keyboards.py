from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def appointment_keyboard(data: dict) -> ReplyKeyboardMarkup:
    used_points = data.get('used_points', 0)
    service_text = data.get('selected_service', {}).get('title', 'не выбрано')
    time_text = data.get('selected_date', 'не выбрано') if 'selected_date' in data else 'не выбрано'
    place_text = data.get('selected_place_type', {}).get('title', 'не выбрано')
    
    kb = ReplyKeyboardBuilder()
    kb.button(text=f"Услуга ({service_text})")
    kb.button(text=f"Списать баллы ({used_points})")
    kb.button(text=f"Время ({time_text})")
    kb.button(text=f"Место проведения ({place_text})")
    kb.button(text="Создать запись")
    kb.button(text="Назад")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)