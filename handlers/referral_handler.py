import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from api.referrals import create_referral
from keyboards.start_keyboards import main_menu_keyboard


logger = logging.getLogger(__name__)
router = Router()

#FSM состояния для фичи
class ReferralState(StatesGroup):
    waiting_for_phone = State()

@router.message(F.text == "Пригласить друга")
async def invite_friend(message:Message,state:FSMContext):
    data = await state.get_data()
    client_id = data.get("client_id")

    if not client_id:
        await message.answer("Ошибка, не удалось найти вашу учетную запись. Попробуйте еще раз. Перезапустите бота (/start).")
        return
    
    back_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад")]],
        resize_keyboard= True
    )

    await message.answer(
        "👥 Введите номер телефона друга. Когда он активирует бота и запишется на первый приём, вам обоим начислится по 500 баллов.\n"
        "Пример ввода: 7 800 555 35 35 или 78005553535",
        reply_markup=back_kb,
    )
    await state.set_state(ReferralState.waiting_for_phone)


@router.message(ReferralState.waiting_for_phone)
async def procces_referral_phone(message:Message,state:FSMContext):
    """
    Обрабатывает введённый текст: если "Назад" — отменяет, иначе пытается создать реферал.
    Убирает пробелы из номера, проверяет простую валидацию (длина и цифры).
    После успеха или ошибки возвращает в главное меню.
    """
    if message.text =="Назад":
        await state.set_state(None)
        await message.answer("😔 Приглашения отменено.", reply_markup=main_menu_keyboard())
        return
    
    data = await state.get_data()
    client_id= data.get("client_id")
    referral_phone = message.text.strip().replace(" ", "")

    if not referral_phone.isdigit() or not (10 <= len(referral_phone) <= 12):
        await message.answer(
            "❌ Некорректный номер. Пример: 78005553535 или 7 800 555 35 35. Попробуйте снова или нажмите 'Назад'.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Назад")]],
                resize_keyboard=True,
            ),
        )
        return
    
    try:
        # Создаём реферал через API
        referral = await create_referral(client_id=client_id, referral_phone=referral_phone,is_active=False)
        logger.info("Referral created for client %s: %s", client_id, referral.id)
        await message.answer(
            f"✅ Друг приглашён! Когда он зарегистрируется и запишется, вы оба получите по 500 баллов. 😊",
            reply_markup=main_menu_keyboard(),
        )
    except Exception as err:
        logger.error("Error creating referral: %s", err)
        error_msg = "Ошибка при приглашении. Возможно, этот номер уже приглашён или проблема с сервером. Попробуйте позже."
        if "unique" in str(err).lower():  # Пример обработки ошибки уникальности, если API возвращает такую
            error_msg = "❌ Этот номер уже приглашён вами или кем-то другим."
        await message.answer(error_msg, reply_markup=main_menu_keyboard())
    
    await state.set_state(None)