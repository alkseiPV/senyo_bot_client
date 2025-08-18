import logging
from datetime import datetime
from typing import List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from api.services_catalog import get_services_list
from api.place_type import get_place_types
from api.appointment import create_appointment
from api.address import create_address
from keyboards.appointment_keyboards import appointment_keyboard
from keyboards.profile_keyboards import profile_keyboard
from keyboards.start_keyboards import main_menu_keyboard
from models.service import ServiceModel
from models.place_type import PlaceTypeModel
from models.address import AddressModel
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove


logger = logging.getLogger(__name__)
router = Router()

class AppointmentStates(StatesGroup):
    menu = State()
    choosing_service = State()
    choosing_place = State()
    choosing_time = State()
    choosing_points = State()
    choosing_address = State()
    waiting_new_address = State()

@router.message(F.text == "Записаться на приём")
async def start_appointment(message: Message, state: FSMContext):
    """Показываем меню записи на приём."""
    data = await state.get_data()
    await message.answer("Записаться на приём:", reply_markup=appointment_keyboard(data))
    await state.set_state(AppointmentStates.menu)


@router.message(AppointmentStates.menu, F.text.regexp(r"^Списать баллы \(.*\)$"))
async def start_choose_points(message: Message, state: FSMContext):
    """Начинаем ввод баллов, но только если услуга выбрана."""
    data = await state.get_data()
    if 'selected_service' not in data:
        await message.answer("Сначала выберите услугу.")
        return
    
    service = data['selected_service']
    available = int(data.get("permanent_points", 0.0) + data.get("temporary_points", 0.0))
    max_deduct = min(available, int(service['price'] * 0.5))
    
    await message.answer(f"Введите количество баллов для списания (0 - {max_deduct}):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AppointmentStates.choosing_points)

@router.message(AppointmentStates.choosing_points)
async def select_points(message: Message, state: FSMContext):
    data = await state.get_data()
    service = data.get('selected_service')  # Recheck, though should exist
    if not service:
        await message.answer("Услуга не выбрана. Возвращаемся.")
        await state.set_state(AppointmentStates.menu)
        await message.answer("", reply_markup=appointment_keyboard(data))
        return
    
    available = int(data.get("permanent_points", 0.0) + data.get("temporary_points", 0.0))
    max_deduct = min(available, int(service['price'] * 0.5))
    
    text = message.text
    if text == "Назад":
        await state.update_data(used_points=None)  # Clear if canceling
        await state.set_state(AppointmentStates.menu)
        data = await state.get_data()
        await message.answer("Выбор баллов отменён.", reply_markup=appointment_keyboard(data))
        return
    
    try:
        val = int(text)
        if not (0 <= val <= max_deduct):
            await message.answer(f"Неверное число. Введите от 0 до {max_deduct}.")
            return
        await state.update_data(used_points=val)
        await state.set_state(AppointmentStates.menu)
        data = await state.get_data()
        await message.answer(f"Баллы для списания: {val}", reply_markup=appointment_keyboard(data))
    except ValueError:
        await message.answer(f"Неверное число. Введите от 0 до {max_deduct}.")
        
        
@router.message(AppointmentStates.menu,F.text.regexp(r"^Услуга \(.*\)$"))
async def start_choose_service(message: Message, state: FSMContext):
    """Начинаем выбор услуги: показываем список из API."""
    try:
        services: List[ServiceModel] = await get_services_list()
        if not services:
            await message.answer("Нет доступных услуг. Попробуйте позже.")
            return
        
        kb_builder = ReplyKeyboardBuilder()
        for service in services:
            kb_builder.button(text=service.title)
        kb_builder.button(text="Назад")
        kb_builder.adjust(1)
        
        await message.answer("Выберите услугу:", reply_markup=kb_builder.as_markup(resize_keyboard=True))
        await state.set_state(AppointmentStates.choosing_service)
    except Exception as e:
        logger.error(f"Ошибка при получении услуг: {e}")
        await message.answer("Произошла ошибка при загрузке услуг.")
        
@router.message(AppointmentStates.choosing_service)
async def select_service(message: Message, state: FSMContext):
    text = message.text
    if text == "Назад":
        await state.set_state(AppointmentStates.menu)
        data = await state.get_data()
        await message.answer("Выбор услуги отменён.", reply_markup=appointment_keyboard(data))
        return
    
    try:
        services: List[ServiceModel] = await get_services_list()
        selected = next((s for s in services if s.title == text), None)
        if not selected:
            await message.answer("Неверный выбор. Попробуйте снова.")
            return
        
        await state.update_data(selected_service=selected.model_dump())
        await state.set_state(AppointmentStates.menu)
        data = await state.get_data()
        await message.answer(f"Услуга выбрана: {selected.title}", reply_markup=appointment_keyboard(data))
    except Exception as e:
        logger.error(f"Ошибка при выборе услуги: {e}")
        await message.answer("Произошла ошибка.")

@router.message(AppointmentStates.menu,F.text.regexp(r"^Время \(.*\)$"))
async def start_choose_time(message: Message, state: FSMContext):
    """Начинаем ввод времени."""
    await message.answer("Введите дату и время в формате YYYY-MM-DD HH:MM (например, 2025-08-17 14:00):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AppointmentStates.choosing_time)

@router.message(AppointmentStates.choosing_time)
async def select_time(message: Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        if dt < datetime.now():
            await message.answer("Дата и время должны быть в будущем. Попробуйте снова (YYYY-MM-DD HH:MM).")
            return  # Остаёмся в том же состоянии для повторного ввода
        
        await state.update_data(selected_date=dt.isoformat())
        await state.set_state(AppointmentStates.menu)
        data = await state.get_data()
        await message.answer(f"Время выбрано: {message.text}", reply_markup=appointment_keyboard(data))
    except ValueError:
        await message.answer("Неверный формат. Попробуйте снова (YYYY-MM-DD HH:MM).")
        

@router.message(AppointmentStates.menu,F.text.regexp(r"^Место проведения \(.*\)$"))
async def start_choose_place(message: Message, state: FSMContext):
    """Начинаем выбор места: показываем список из API."""
    try:
        place_types: List[PlaceTypeModel] = await get_place_types()
        if not place_types:
            await message.answer("Нет доступных мест. Попробуйте позже.")
            return
        
        kb_builder = ReplyKeyboardBuilder()
        for place in place_types:
            kb_builder.button(text=place.title)
        kb_builder.button(text="Назад")
        kb_builder.adjust(1)
        
        await message.answer("Выберите место проведения:", reply_markup=kb_builder.as_markup(resize_keyboard=True))
        await state.set_state(AppointmentStates.choosing_place)
    except Exception as e:
        logger.error(f"Ошибка при получении мест: {e}")
        await message.answer("Произошла ошибка при загрузке мест.")

@router.message(AppointmentStates.choosing_place)
async def select_place(message: Message, state: FSMContext):
    text = message.text
    if text == "Назад":
        await state.set_state(AppointmentStates.menu)
        data = await state.get_data()
        await message.answer("Выбор места отменён.", reply_markup=appointment_keyboard(data))
        return
    
    try:
        place_types: List[PlaceTypeModel] = await get_place_types()
        selected = next((p for p in place_types if p.title == text), None)
        if not selected:
            await message.answer("Неверный выбор. Попробуйте снова.")
            return
        
        await state.update_data(selected_place_type=selected.model_dump(), selected_address_id=None)
        await state.set_state(AppointmentStates.menu)
        data = await state.get_data()
        await message.answer(f"Место выбрано: {selected.title}", reply_markup=appointment_keyboard(data))
        
        if "дом" in selected.title.lower():
            await start_choose_address(message, state)
    except Exception as e:
        logger.error(f"Ошибка при выборе места: {e}")
        await message.answer("Произошла ошибка.")
        
async def start_choose_address(message: Message, state: FSMContext):
    """Начинаем выбор адреса."""
    data = await state.get_data()
    addresses = data.get("addresses", [])
    if not addresses:
        await message.answer("У вас нет сохранённых адресов. Введите новый адрес:")
        await state.set_state(AppointmentStates.waiting_new_address)
        return
    
    text = "Выберите адрес (введите номер):\n"
    for i, addr in enumerate(addresses, 1):
        text += f"{i}. {addr['address']}\n"
    
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(AppointmentStates.choosing_address)
    
@router.message(AppointmentStates.choosing_address)
async def select_address(message: Message, state: FSMContext):
    text = message.text.lower()
    data = await state.get_data()
    addresses = data.get("addresses", [])
    
    
    try:
        idx = int(text) - 1
        selected = addresses[idx]
        await state.update_data(selected_address_id=selected['id'])
        await state.set_state(AppointmentStates.menu)
        data = await state.get_data()
        await message.answer(f"Адрес выбран: {selected['address']}", reply_markup=appointment_keyboard(data))
    except (ValueError, IndexError):
        await message.answer("Неверный выбор. Попробуйте снова.")

@router.message(AppointmentStates.waiting_new_address)
async def add_new_address(message: Message, state: FSMContext):
    address_str = message.text.strip()
    if not address_str:
        await message.answer("Адрес не может быть пустым. Попробуйте снова.")
        return
    
    try:
        data = await state.get_data()
        client_id = data.get("client_id")
        if not client_id:
            await message.answer("Ошибка: ID клиента не найден.")
            return
        
        new_addr: AddressModel = await create_address(client_id, address_str)
        addresses = data.get("addresses", []) + [new_addr.model_dump()]
        await state.update_data(addresses=addresses, selected_address_id=new_addr.id)
        await state.set_state(AppointmentStates.name)
        data = await state.get_data()
        await message.answer(f"Адрес добавлен и выбран: {address_str}", reply_markup=appointment_keyboard(data))
    except Exception as e:
        logger.error(f"Ошибка при добавлении адреса: {e}")
        await message.answer("Произошла ошибка при добавлении адреса.")

@router.message(AppointmentStates.menu,F.text == "Создать запись")
async def create_appointment_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    required_keys = ['selected_service', 'selected_date', 'selected_place_type']
    if not all(key in data for key in required_keys):
        await message.answer("Не все данные выбраны. Заполните все поля.")
        return
    
    try:
        service = data['selected_service']
        place = data['selected_place_type']
        requires_address = "дом" in place['title'].lower()
        address_id = data.get('selected_address_id')
        
        if requires_address and address_id is None:
            await message.answer("Для этого места требуется адрес. Выберите его.")
            await start_choose_address(message, state)
            return
        
        used_points = data.get('used_points', 0)
        final_sum = service['price'] - used_points  # Both int
        
        await create_appointment(
            id_client=data['client_id'],
            id_address=address_id,
            final_sum=final_sum,
            id_service=service['id'],
            id_place_type=place['id'],
            date_iso=data['selected_date']
        )
        
        await message.answer("Запись успешно создана!")
        
        # Clear appointment data
        keys_to_keep = ['client_id', 'phone', 'gender', 'permanent_points', 'temporary_points', 'addresses']
        new_data = {k: data[k] for k in keys_to_keep if k in data}
        await state.set_data(new_data)
        await state.set_state(None)
        await message.answer("Возращаемся в главное меню", reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error(f"Ошибка при создании записи: {e}")
        await message.answer("Произошла ошибка при создании записи.")