from aiogram.types import ReplyKeyboardMarkup,KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def promotions_back_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Назад")
    return kb.as_markup(resize_keyboard=True)