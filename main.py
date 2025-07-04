import asyncio
from config import settings
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from api import base_api  
from middlewares.backend import BackendMiddleware
from handlers import start_handler

async def main():
    bot = Bot(settings.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_router(start_handler.router)
    dp.update.outer_middleware(BackendMiddleware(base_api))
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await base_api.close()

if __name__=='__main__':
    asyncio.run(main())