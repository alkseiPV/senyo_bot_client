import logging

from aiogram import Router, F
from aiogram.types import Message

from api.promotions import get_promotions
from keyboards.promotions_keyboard import promotions_back_keyboard
from keyboards.start_keyboards import main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text.casefold() =='промоакции')
async def show_promotions(message:Message):
    try:
        promotions = await get_promotions()
        if not promotions:
            await message.answer(
                "На данный момент активных промоакций нет.",
                reply_markup=promotions_back_keyboard(),
            )
            return
        promo_text = "Доступные промоакции: \n\n"
        for promo in promotions:
            promo_text += (
                f"**{promo.title}**\n"
                f"{promo.description}\n"
                f"Баллы: {promo.added_points}\n"
                f"Для: {promo.gender}\n"
                f"С {promo.start_date.strftime('%d.%m.%Y')} по {promo.expiration_date.strftime('%d.%m.%Y')}\n\n"
            )
        await message.answer(
            promo_text,
            reply_markup=promotions_back_keyboard(),
            parse_mode="Markdown",
        )
    except Exception as err:
        logger.error("Ошибка при получении промоакций: %s",err)
        await message.answer(
            "Произошла ошибка при загрузке промоакций. Попробуйте позже. ",
            reply_markup=promotions_back_keyboard(),
        )

# @router.message(F.text.casefold() == "назад")
# async def go_back(message: Message):
#     await message.answer("Главное меню.", reply_markup=main_menu_keyboard())