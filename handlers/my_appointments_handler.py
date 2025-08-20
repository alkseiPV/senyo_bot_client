import logging
from typing import List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from api.appointment import cancel_appointment

from api.appointment import get_appointments
from models.appointment import AppointmentModel
from keyboards.start_keyboards import main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router()

class MyAppointments(StatesGroup):
    viewing = State()
    canceling = State()
    
@router.message(F.text == "Мои записи")
async def show_my_appointments(message: Message, state: FSMContext):
    data =  await state.get_data()
    client_id = data.get("client_id")
    if not client_id:
        await message.answer("Ошибка: ID клиента не найден. Вернитесь в /start.")
        return
    
    try: 
        appointments: List[AppointmentModel] = await get_appointments(client_id = client_id)
        active_appointments = [app for app in appointments if app.status in ["ожидание", "подтвержден"]]
        
        if not active_appointments:
            text = "😔 У вас нет активных записей."
        else:
            text = "📅 Ваши активные записи: \n\n"
            active_appointments.sort(key=lambda a: a.date)
            for app in active_appointments:
                status_text = "подтверждена" if app.status == "подтвержден" else "ожидание"
                time_str = app.date.strftime("%d.%m.%Y %H:%M")
                text += f"{time_str}\n{app.service_name} ({status_text})\n\n"
        
        keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отменить запись")],
                [KeyboardButton(text="Назад")],], resize_keyboard=True)
        await message.answer(text, reply_markup=keyboard)
        await state.set_state(MyAppointments.viewing)
    except Exception as e:
        logger.error(f"Ошибка при получении записей: {e}")
        await message.answer("Произошла ошибка. попробуйте позже.")
        await state.set_state(None)
        
@router.message(MyAppointments.viewing, F.text == "Назад")
async def back_to_main(message: Message, state: FSMContext):
    """Возвращает в главное меню."""
    await message.answer("Возвращаемся в главное меню:", reply_markup=main_menu_keyboard())
    await state.set_state(None)

@router.message(MyAppointments.viewing, F.text =="Отменить запись")
async def start_cancel(message: Message, state:FSMContext):
    data = await state.get_data()
    client_id = data.get("client_id")
    if not client_id:
        await message.answer("Ошибка: ID клиента не найден. Вернитесь в /start.")
        return
    
    try:
        appointments: List[AppointmentModel] = await get_appointments(client_id=client_id)
        active_appointments = [app for app in appointments if app.status in ["ожидание", "подтвержден"]]
        
        if not active_appointments:
            await message.answer("😔 Нет записей для отмены.")
            await state.set_state(MyAppointments.viewing)  # Остаёмся в viewing
            return

        inline_kb = InlineKeyboardMarkup(inline_keyboard=[])
        for app in sorted(active_appointments, key=lambda a: a.date):
            time_str = app.date.strftime("%d.%m.%Y %H:%M")
            inline_kb.inline_keyboard.append(
                [InlineKeyboardButton(text=time_str, callback_data=f"cancel_{app.id}")]
            )
        await message.answer("🗑 Выберите запись для отмены:", reply_markup= inline_kb)
        await state.set_state(MyAppointments.canceling)
    except Exception as e:
        logger.error(f"Ошибка при подготовке отмены: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
        await state.set_state(None)
        
@router.callback_query(MyAppointments.canceling, F.data.startswith("cancel_"))
async def cancel_appointment_callback(callback: CallbackQuery, state: FSMContext):
    try:
        app_id = int(callback.data.split("_")[1])  # Парсим ID записи из callback_data
        await cancel_appointment(appointment_id=app_id)  # Вызов API для отмены
        await callback.message.delete()  # Удаляем сообщение с inline-клавиатурой
        await callback.answer("✅ Запись отменена успешно.")  # Показываем попап-уведомление
        await callback.message.answer("✅ Запись отменена. Возвращаемся в главное меню:", reply_markup=main_menu_keyboard())
        await state.set_state(None)  # Сбрасываем состояние
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке callback: {e}")
        await callback.answer("❌ Произошла ошибка при отмене. Попробуйте позже.")
            