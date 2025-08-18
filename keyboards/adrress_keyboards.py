from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from models.address import AddressModel

def addresses_main_keyboard(has_addresses: bool = True) -> ReplyKeyboardMarkup:
    """
    Основная reply-клавиатура: "Добавить", "Удалить" (если адреса есть), "Назад".
    """
    kb = ReplyKeyboardBuilder()
    kb.button(text="Добавить")
    if has_addresses:
        kb.button(text="Удалить")
    kb.button(text="Назад")
    kb.adjust(1)  # Каждая кнопка в отдельном ряду
    return kb.as_markup(resize_keyboard=True)

def back_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Reply-клавиатура только с "Назад" (для экранов ввода и удаления).
    """
    kb = ReplyKeyboardBuilder()
    kb.button(text="Назад")
    return kb.as_markup(resize_keyboard=True)

def delete_addresses_inline_keyboard(addresses: List[AddressModel]) -> InlineKeyboardMarkup:
    """
    Inline-клавиатура только для удаления: Кнопки с адресами (каждый в отдельном ряду).
    """
    kb = InlineKeyboardBuilder()
    for addr in addresses:
        kb.button(text=addr.address, callback_data=f"delete_addr_{addr.id}")
    return kb.as_markup()