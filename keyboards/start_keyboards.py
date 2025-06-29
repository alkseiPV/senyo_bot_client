from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def initial_keyboard() -> ReplyKeyboardMarkup:
    """
    Кнопки:
        📞 Поделиться номером  (request_contact=True)
        🚻 Выбрать пол
    """
    kb = ReplyKeyboardBuilder()
    kb.button(text="📞 Поделиться номером", request_contact=True)
    kb.button(text="🚻 Выбрать пол")
    return kb.as_markup(resize_keyboard=True)


def gender_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Мужской")
    kb.button(text="Женский")
    return kb.as_markup(resize_keyboard=True)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="ПРОФИЛЬ")
    kb.button(text="Записаться на приём")
    kb.button(text="Проверить баланс")
    kb.button(text="Пригласить друга")
    kb.button(text="ПРОМОАКЦИИ")
    kb.button(text="Мои записи")
    kb.adjust(1)  # каждая кнопка в своём ряду
    return kb.as_markup(resize_keyboard=True)
