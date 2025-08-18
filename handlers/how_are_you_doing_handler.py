from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove



router = Router()

# @router.message(Command("start"))
# async def cmd_start(message:Message):
#     await message.answer("Как у вас дела?", reply_markup=how_are_you_doing_kb())

@router.message(F.text.lower() == "великолепно")
async def answer_yes(message:Message):
    await message.answer("Рад за вас)", reply_markup=ReplyKeyboardRemove())

@router.message(F.text.lower() == "плохо")
async def answer_yes(message:Message):
    await message.answer("печалька", reply_markup=ReplyKeyboardRemove())