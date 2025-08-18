from aiogram import Router,F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from api.client import get_client_info
from models.client import ClientModel
from keyboards.start_keyboards import main_menu_keyboard

router = Router()

@router.message(F.text =="Проверить баланс")
async def check_balance(message:Message,state: FSMContext):
    # получаем данные из FSM
    data = await state.get_data()
    client_id = data.get("client_id")
    if not client_id:
        await message.answer("Ошибка: данные не найдены. Перезапустите бота (/start).")
        return
    
    # Вызываем АПИ для получения данных клиента
    try:
        client_data = await get_client_info(client_id=client_id,is_telegram=False)
        client = client_data
    except Exception as e:
        await message.answer(f"Ошибка при запросе к backend: {str(e)}")
        return
    
    response = (
        f"Ваш баланс:\n"
        f"Постоянные баллы: {client.permanent_points}\n"
        f"Временные баллы: {client.temporary_points}"
    )

    await message.answer(response,reply_markup=main_menu_keyboard())
    