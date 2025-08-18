import logging
from typing import Any, Dict

from aiohttp import ClientResponseError
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from api import (
    register_client,
    get_client_info,
    update_client,
)
from keyboards.start_keyboards import (
    initial_keyboard,
    gender_keyboard,
    main_menu_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()


# ──────────────────────────
#   /start
# ──────────────────────────
@router.message(Command("start"))
async def cmd_start(
    message: Message,
    state: FSMContext,
):
    """Создаём/получаем клиента, спрашиваем телефон и пол, или показываем меню."""
    await state.clear()  # сброс прошлых данных

    tg_id = message.from_user.id

    # 1) получаем клиента, регистрируем при необходимости
    try:
        client = await get_client_info(tg_id, is_telegram=True)
    except ClientResponseError as err:
        # не найден ⇒ регистрируем
        if err.status == 500:
            logger.info("User %s not found, registering", tg_id)
            await register_client(tg_id)
            client = await get_client_info(tg_id, is_telegram=True)
        else:
            raise

    # 2) кладём нужные поля в FSM-state (можно доставать в других хендлерах)
    await state.update_data(
        client_id=client.id,
        phone=client.phone or "",
        gender=client.gender or "",
        permanent_points=client.permanent_points,
        temporary_points=client.temporary_points,
       addresses=[addr.model_dump() for addr in client.addresses],
    )

    # 3) выясняем, что ещё нужно спросить
    missing_phone = not client.phone
    missing_gender = not client.gender

    if missing_phone or missing_gender:
        await message.answer(
            "Для продолжения пришлите ваш номер и выберите пол:",
            reply_markup=initial_keyboard(),
        )
    else:
        await message.answer(
            "С возвращением! Выберите действие:",
            reply_markup=main_menu_keyboard(),
        )


# ──────────────────────────
#   Пришёл номер телефона
# ──────────────────────────
@router.message(F.contact)
async def contact_received(message: Message, state: FSMContext):
    """Обновляем номер в БД и в FSM."""
    phone = message.contact.phone_number
    data = await state.get_data()

    await update_client(id=data["client_id"], phone=phone)
    await state.update_data(phone=phone)

    # Проверяем, нужен ли ещё пол
    if not data.get("gender"):
        await message.answer(
            "Спасибо! Теперь выберите пол:",
            reply_markup=gender_keyboard(),
        )
    else:
        await message.answer(
            "Данные обновлены. Что делаем дальше?",
            reply_markup=main_menu_keyboard(),
        )


# ──────────────────────────
#   Пользователь нажал «Выбрать пол» или сам пол
# ──────────────────────────
@router.message(F.text.casefold() == "🚻 выбрать пол")
async def ask_gender(message: Message):
    await message.answer("Выберите пол:", reply_markup=gender_keyboard())


@router.message(F.text.in_(["Мужской", "Женский"]))
async def gender_chosen(message: Message, state: FSMContext):
    selected = message.text
    gender_id = 1 if selected == "Мужской" else 2  # ID справочника полов

    data = await state.get_data()
    await update_client(id=data["client_id"], gender=gender_id)   # ⬅ строка
    await state.update_data(gender=gender_id)

    # Если номера ещё нет, ждём его; иначе — в главное меню
    if not data.get("phone"):
        await message.answer(
            "Пол сохранён. Пришлите, пожалуйста, номер телефона 👇",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📞 Поделиться номером", request_contact=True)]],
                resize_keyboard=True,
            ),
        )
    else:
        await message.answer(
            "Отлично! Данные обновлены.",
            reply_markup=main_menu_keyboard(),
        )
