from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def profile_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Изменить фамилию и имя")
    kb.button(text="Все записи (архив)")
    kb.button(text="Мои адреса")
    kb.button(text="Мои друзья (приглашенные)")
    kb.button(text="Назад")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)