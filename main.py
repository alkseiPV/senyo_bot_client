import asyncio
from config import settings
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from api.client import backend
from middlewares.backend import BackendMiddleware
from handlers import how_are_you_doing_handler

async def main():
    bot = Bot(settings.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_router(how_are_you_doing_handler.router)
    dp.update.outer_middleware(BackendMiddleware(backend))
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await backend.close()

if __name__=='__main__':
    asyncio.run(main())