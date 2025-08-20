import logging
from typing import Any, Dict,List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from api.client import update_client 
from keyboards.profile_keyboards import profile_keyboard 
from keyboards.start_keyboards import main_menu_keyboard  

from datetime import datetime
from api.appointment import get_appointments
from models.appointment import AppointmentModel
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers import address_handler

from api.referrals import get_referrals
from models.referral import ReferralsModel
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


logger = logging.getLogger(__name__)
router = Router()

class EditFIO(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()

class Archive(StatesGroup):
    waiting_for_month = State()

class Friends(StatesGroup):
    viewing_friends = State()

@router.message(F.text == "ПРОФИЛЬ")
async def show_profile(message:Message,state: FSMContext):
    await message.answer("👤 Ваш профиль:", reply_markup=profile_keyboard())

#──────────────────────────
#   Изменить ФИО
# ──────────────────────────
@router.message(F.text == "Изменить ФИО")
async def start_edit_fio(message: Message, state: FSMContext):
    """Начинаем процесс изменения ФИО, показываем текущее и клавиатуру 'Назад'."""
    data = await state.get_data()
    current_name = data.get("name", "Не указано")  # Берём из FSM, default если нет
    current_surname = data.get("surname", "Не указано")
    
    await message.answer(
        f"👤 Текущее ФИО: {current_name} {current_surname}.\nВведите ваше имя:",
        reply_markup=back_keyboard()  # ← Keyboard с "Назад" вместо Remove
    )
    await state.set_state(EditFIO.waiting_for_name)
    
@router.message(EditFIO.waiting_for_name, F.text == "Назад")
@router.message(EditFIO.waiting_for_surname, F.text == "Назад")
async def cancel_edit_fio(message: Message, state: FSMContext):
    """Отмена изменения ФИО, возврат в профиль."""
    await state.set_state(None)  # Очищаем состояние (как указано в стиле: state.set_state(None) вместо clear)
    await message.answer("❌ Изменение ФИО отменено.", reply_markup=profile_keyboard())

@router.message(EditFIO.waiting_for_name)
async def receive_name(message: Message, state: FSMContext):
    """Сохраняем имя и просим фамилию с клавиатурой 'Назад'."""
    name = message.text.strip()
    if not name:
        await message.answer("❌ Имя не может быть пустым. Попробуйте снова:", reply_markup=back_keyboard())
        return
    await state.update_data(new_name=name)
    await message.answer("Теперь введите вашу фамилию:", reply_markup=back_keyboard())  # ← Добавлен keyboard
    await state.set_state(EditFIO.waiting_for_surname)

@router.message(EditFIO.waiting_for_surname)
async def receive_surname_and_update(message: Message, state: FSMContext):
    """Сохраняем фамилию, обновляем в БД и возвращаем в профиль."""
    surname = message.text.strip()
    data = await state.get_data()
    client_id = data.get("client_id")  # Берем из глобального state (из start_handler)
    if not client_id:
        await message.answer("Ошибка: ID клиента не найден. Вернитесь в /start.")
        await state.set_state(None)
        return

    try:
        await update_client(id=client_id, name=data["new_name"], surname=surname)
        await state.update_data(name=data["new_name"], surname=surname)  # Обновляем в FSM для будущего использования
        await message.answer("ФИО обновлено!", reply_markup=profile_keyboard())
        await state.set_state(None)
    except Exception as e:
        logger.error(f"Ошибка обновления ФИО: {e}")
        await message.answer("Произошла ошибка при обновлении. Попробуйте позже.")



# ──────────────────────────
#   Назад (возврат в главное меню)
# ──────────────────────────
@router.message(F.text == "Назад")
async def go_back(message: Message, state: FSMContext):
    """Возвращаем в зависимости от состояния: из архива — в профиль, иначе — в главное меню."""
    current_state = await state.get_state()
    if current_state in [Archive.waiting_for_month.state, Friends.viewing_friends.state]:
        await message.answer("Возвращаемся в профиль:", reply_markup=profile_keyboard())
        await state.set_state(None)
    else:
        await message.answer("Возвращаемся в главное меню:", reply_markup=main_menu_keyboard())
    await state.set_state(None)

# ──────────────────────────
#   Заглушки для остальных кнопок (до предоставления API/моделей)
# ──────────────────────────
@router.message(F.text == "Все записи (архив)")
async def all_records(message: Message, state: FSMContext):
    data = await state.get_data()
    client_id = data.get("client_id")
    if not client_id:
        await message.answer("Ошибка: ID клиента не найден. Вернитесь в /start.")
        return
    
    try:
        appointments = await get_appointments(client_id=client_id)
        if not appointments:
            await message.answer("😔 У вас нет записей.", reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Назад")]],
                resize_keyboard=True,
            ))
            await state.set_state(Archive.waiting_for_month)
            return
        
        appointments.sort(key = lambda a: a.date, reverse=True)
        recent = appointments[:20]

        text = "Для получения записей за опр. месяц введите его в чат, Пример: Март 2025\n\nВаши последние (20) записи:\n"
        for app in recent:
            points_text =f"✅ Начислено {app.client_points} баллов" if app.used_points is None else f"Использовано {app.used_points} баллов"
            text += f"{app.date.strftime('%d.%m.%Y')} - {app.service_name} {app.final_sum} руб ({points_text})\n"
            
        await message.answer(text, reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Назад")]],
            resize_keyboard=True,
        ))
        await state.set_state(Archive.waiting_for_month)
    except Exception as e:
        logger.error(f"Ошибка при получении записей: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
        await state.set_state(None)


@router.message(Archive.waiting_for_month)
async def filter_by_month(message:Message, state:FSMContext):
    month_input = message.text.strip().capitalize()

    months_dict = {
        "Январь": 1, "Февраль": 2, "Март": 3, "Апрель": 4, "Май": 5, "Июнь": 6,
        "Июль": 7, "Август": 8, "Сентябрь": 9, "Октябрь": 10, "Ноябрь": 11, "Декабрь": 12
    }

    data = await state.get_data()
    client_id = data.get("client_id")
    if not client_id:
        await message.answer("Ошибка: ID клиента не найден. Вернитесь в /start.")
        return
    try:
        appointments = await get_appointments(client_id=client_id)
        if not appointments:
            await message.answer("😔 У вас нет записей.")
            await state.set_state(None)
            return
        
        parts = month_input.split()
        if len(parts) !=2:
            raise ValueError("Неверный формат.")
        month_name = parts[0]
        year = int(parts [1])
        month_num = months_dict.get(month_name)
        if not month_num:
            raise ValueError("Неверный месяц.")
        
        filtered = [app for app in appointments if app.date.month == month_num and app.date.year == year]
        if not filtered:
            await message.answer(f"😔 Нет записей за {month_input}.")
            return

        text = f"📅 Записи за {month_input}:\n"
        for app in filtered:
            points_text = f"Начислено {app.client_points} баллов" if app.used_points is None else f"Использовано {app.used_points} баллов"
            text += f"{app.date.strftime('%d.%m.%Y')} - {app.service_name} {app.final_sum} руб ({points_text})\n"

        await message.answer(text)
    except ValueError:
        # Неверный формат — показываем ошибку и последние 20
        appointments.sort(key=lambda a: a.date, reverse=True)
        recent = appointments[:20]
        text = "Неверный формат. Пример: Март 2025\n\nВаши последние (20) записи:\n"
        for app in recent:
            points_text = f"Начислено {app.client_points} баллов" if app.used_points is None else f"Использовано {app.used_points} баллов"
            text += f"{app.date.strftime('%d.%m.%Y')} - {app.service_name} {app.final_sum} руб ({points_text})\n"
        await message.answer(text)
    except Exception as e:
        logger.error(f"Ошибка при фильтрации записей: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")



@router.message(F.text == "Мои друзья (приглашенные)")
async def my_friends(message: Message,state: FSMContext):
    data = await state.get_data()
    client_id = data.get("client_id")
    if not client_id:
        await message.answer("Ошибка: ID клиента не найден. Вернитесь в /start.")
        return
    
    try:
        referrals: List[ReferralsModel] = await get_referrals(client_id)
        if not referrals:
            text = "😔 У вас нет приглашенных друзей."
            
        else: 
            text = "👥 Ваши друзья:\n"
            for ref in referrals:
                status = "(активирован)" if ref.is_active else "(не активирован)"
            text += f"{ref.referral_phone} {status}\n"

        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Назад")]],
            resize_keyboard=True,
        )
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(Friends.viewing_friends)
    except Exception as e:
        logger.error(f"Ошибка при получении друзей: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
        await state.set_state(None)
        
def back_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой 'Назад' для отмены изменений."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад")]],
        resize_keyboard=True,
    )