import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db
from handlers import admin, corruption, personal, reception, start

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # DIQQAT: start.router birinchi bo'lishi kerak - "❌ Bekor qilish" tugmasi
    # har qanday holatda (state) to'g'ri ishlashi uchun.
    dp.include_router(start.router)
    dp.include_router(corruption.router)
    dp.include_router(personal.router)
    dp.include_router(reception.router)
    dp.include_router(admin.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
