import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from config import BOT_TOKEN
from database.db import init_db
from handlers import admin, corruption, personal, reception, start

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    @dp.errors()
    async def error_handler(event: ErrorEvent):
        """Kutilmagan xatolik yuz berganda: logga yozadi va, agar callback tugma
        bosilgan bo'lsa, uni javobsiz qoldirmaydi (aks holda tugma 'yuklanmoqda'
        holatida abadiy qotib qoladi)."""
        logging.exception("Xatolik yuz berdi: %s", event.exception)
        update = event.update
        if update.callback_query:
            try:
                await update.callback_query.answer(
                    "Xatolik yuz berdi, iltimos qaytadan urinib ko'ring.",
                    show_alert=True,
                )
            except Exception:
                pass

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
