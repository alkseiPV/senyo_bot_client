import logging
from typing import List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from aiogram.filters import StateFilter

from api.client import get_client_info  # Для перезапроса клиента
from api.address import create_address, delete_address  # API для адресов
from models.address import AddressModel  # Модель адреса
from keyboards.adrress_keyboards import  addresses_main_keyboard, back_reply_keyboard, delete_addresses_inline_keyboard

from keyboards.profile_keyboards import profile_keyboard  # Для возврата в профиль

logger = logging.getLogger(__name__)
router = Router()

# FSM для адресов
class Addresses(StatesGroup):
    my_addresses = State()
    waiting_for_new_address = State()  # Ожидание ввода нового адреса
    in_delete_mode = State()  # В режиме удаления (для хранения message_id)

@router.message(F.text == "Мои адреса")
async def show_addresses(message: Message, state: FSMContext):
    """Показываем нумерованный список адресов в тексте и reply-клавиатуру."""
    tg_id = message.from_user.id
    await state.set_state(None)

    try:
        # Перезапрашиваем клиента для свежих данных
        client = await get_client_info(tg_id, is_telegram=True)
        addresses: List[AddressModel] = client.addresses
        await state.update_data(addresses=addresses, client_id=client.id)

        if not addresses:
            text = "У вас нет сохранённых адресов."
            keyboard = addresses_main_keyboard(has_addresses=False)
        else:
            text = "Ваши адреса:\n"
            for i, addr in enumerate(addresses, start=1):
                text += f"{i}. {addr.address}\n"
            await state.set_state(Addresses.my_addresses)
            keyboard = addresses_main_keyboard(has_addresses=True)

        await message.answer(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при получении адресов: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.", reply_markup=profile_keyboard())
        await state.set_state(None)
        
@router.message(Addresses.waiting_for_new_address, F.text == "Назад")
@router.message(Addresses.in_delete_mode, F.text == "Назад")
async def go_back_from_substates(message: Message, state: FSMContext):
    """Возвращаем из добавления/удаления в основной экран адресов."""
    # Удаляем сообщение удаления, если оно есть
    data = await state.get_data()
    delete_message_id = data.get("delete_message_id")
    if delete_message_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
        except:
            pass
    await message.answer("Возвращаемся к списку адресов.")
    await show_addresses(message, state)
        
@router.message(StateFilter( Addresses.my_addresses), F.text == "Назад")
async def go_back_from_my_addresses(message: Message, state: FSMContext):
    """Возвращаем из my_addresses в профиль."""
    await state.set_state(None)
    await message.answer("Возвращаемся в профиль:", reply_markup=profile_keyboard())

# ──────────────────────────
#   Добавить адрес (reply)
# ──────────────────────────
@router.message(F.text == "Добавить")
async def start_add_address(message: Message, state: FSMContext):
    """Просим ввести новый адрес с reply 'Назад'."""
    await message.answer(
        "Введите свой адрес с городом. Пример: Москва, ул Пушкина д30 к22",
        reply_markup=back_reply_keyboard(),
    )
    await state.set_state(Addresses.waiting_for_new_address)

@router.message(Addresses.waiting_for_new_address)
async def receive_new_address(message: Message, state: FSMContext):
    """Создаём адрес, обновляем state и возвращаем к основному экрану."""
    new_address = message.text.strip()
    if new_address == "Назад":
        state.set_state(Addresses.my_addresses)
        await show_addresses(message, state)
    if not new_address:
        await message.answer("Адрес не может быть пустым. Попробуйте снова:")
        return

    data = await state.get_data()
    client_id = data.get("client_id")
    if not client_id:
        await message.answer("Ошибка: ID клиента не найден. Вернитесь в 'Мои адреса'.")
        
        return

    try:
        created = await create_address(client_id, new_address)
        addresses: List[AddressModel] = data.get("addresses", [])
        addresses.append(created)
        await state.update_data(addresses=addresses)

        await message.answer("Адрес добавлен!")
        # Возврат к основному экрану с обновленным списком
        await show_addresses(message, state)
    except Exception as e:
        logger.error(f"Ошибка при добавлении адреса: {e}")
        await message.answer("Произошла ошибка при добавлении. Попробуйте позже.")

# ──────────────────────────
#   Удалить адрес (reply) — вход в режим удаления с inline
# ──────────────────────────
@router.message(F.text == "Удалить")
async def start_delete_addresses(message: Message, state: FSMContext):
    """Отправляем сообщение с inline-кнопками адресов для удаления и reply 'Назад'."""
    data = await state.get_data()
    addresses: List[AddressModel] = data.get("addresses", [])
    if not addresses:
        await message.answer("Нет адресов для удаления.", reply_markup=addresses_main_keyboard(has_addresses=False))
        await state.set_state(None)
        return

    text = "Выберите адрес для удаления (нажмите на кнопку):"
    sent_message = await message.answer(text, reply_markup=delete_addresses_inline_keyboard(addresses))
    await state.update_data(delete_message_id=sent_message.message_id)
    await state.set_state(Addresses.in_delete_mode)

# ──────────────────────────
#   Callback: Удалить адрес (inline)
# ──────────────────────────
@router.callback_query(Addresses.in_delete_mode, F.data.startswith("delete_addr_"))
async def delete_address_callback(callback: CallbackQuery, state: FSMContext):
    """Удаляем адрес, обновляем inline-сообщение. Если адресов 0 — возврат к основному экрану."""
    await callback.answer("Удаляем...")  # Показываем пользователю
    addr_id = int(callback.data.split("delete_addr_")[1])

    data = await state.get_data()
    addresses: List[AddressModel] = data.get("addresses", [])
    delete_message_id = data.get("delete_message_id")
    if not delete_message_id:
        await callback.message.answer("Ошибка: Сессия утеряна. Вернитесь в 'Мои адреса'.")
        return

    try:
        # Удаляем из БД и из списка
        await delete_address(addr_id)
        addresses = [addr for addr in addresses if addr.id != addr_id]
        await state.update_data(addresses=addresses)

        if not addresses:
            # Нет адресов — возврат к основному экрану
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=delete_message_id)
            await callback.message.answer("Все адреса удалены.")
            await show_addresses(callback.message, state)  # callback.message как Message
        else:
            # Обновляем inline-сообщение
            new_text = "Выберите адрес для удаления (нажмите на кнопку):"
            await callback.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=delete_message_id,
                text=new_text,
                reply_markup=delete_addresses_inline_keyboard(addresses),
            )
            
    except Exception as e:
        logger.error(f"Ошибка при удалении адреса: {e}")
        await callback.message.answer("Произошла ошибка при удалении. Попробуйте позже.")
        


# ──────────────────────────
#   Назад (reply) — из любого состояния
# ──────────────────────────
# @router.message(F.text == "Назад")
# async def go_back(message: Message, state: FSMContext):
#     """Возвращаем в зависимости от состояния: из добавления/удаления — в основной экран адресов, иначе — в профиль."""
#     current_state = await state.get_state()
#     if current_state in [Addresses.waiting_for_new_address.state, Addresses.in_delete_mode.state]:
#         # Удаляем сообщение удаления, если оно есть
#         data = await state.get_data()
#         delete_message_id = data.get("delete_message_id")
#         if delete_message_id:
#             try:
#                 await message.bot.delete_message(chat_id=message.chat.id, message_id=delete_message_id)
#             except:
#                 pass
#         await message.answer("Возвращаемся к списку адресов.")
#         await state.set_state(None)

#         await show_addresses(message, state)
#     else:
#         await state.set_state(None)
#         await message.answer("Возвращаемся в профиль:", reply_markup=profile_keyboard())