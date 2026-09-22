from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import SUPERADMIN_IDS
from database.models import create_appeal
from keyboards.inline import appeal_admin_kb
from keyboards.reply import cancel_kb, main_menu_kb
from utils.states import CorruptionStates

router = Router()


@router.message(F.text == "🔴 Korrupsiyaga guvoh bo'ldim")
async def start_corruption(message: Message, state: FSMContext):
    await state.set_state(CorruptionStates.waiting_text)
    await message.answer(
        "Guvohi bo'lgan holatni batafsil yozib yuboring.\n"
        "Xohlasangiz rasm yoki hujjat ham biriktirishingiz mumkin.\n\n"
        "⚠️ Bu bo'limda ro'yxatdan o'tish talab qilinmaydi. "
        "Murojaatingiz faqat superadminga yetib boradi.",
        reply_markup=cancel_kb(),
    )


@router.message(CorruptionStates.waiting_text)
async def receive_corruption(message: Message, state: FSMContext):
    text = message.caption or message.text or ""
    file_id, file_type = None, None
    if message.photo:
        file_id, file_type = message.photo[-1].file_id, "photo"
    elif message.document:
        file_id, file_type = message.document.file_id, "document"

    appeal_id = await create_appeal(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        appeal_type="corruption",
        text=text,
        file_id=file_id,
        file_type=file_type,
    )

    await state.clear()
    await message.answer(
        f"✅ Murojaatingiz qabul qilindi. Murojaat raqami: #{appeal_id}",
        reply_markup=main_menu_kb(),
    )

    admin_text = (
        f"🔴 <b>YANGI KORRUPSIYA MUROJAATI</b> #{appeal_id}\n\n"
        f"Yuboruvchi ID: <code>{message.from_user.id}</code>\n"
        f"Username: @{message.from_user.username or 'mavjud emas'}\n\n"
        f"Matn: {text or '(matn kiritilmagan)'}"
    )

    for admin_id in SUPERADMIN_IDS:
        try:
            if file_id and file_type == "photo":
                await message.bot.send_photo(admin_id, file_id, caption=admin_text)
            elif file_id and file_type == "document":
                await message.bot.send_document(admin_id, file_id, caption=admin_text)
            else:
                await message.bot.send_message(admin_id, admin_text)
            await message.bot.send_message(
                admin_id,
                f"#{appeal_id} bo'yicha javob yozish uchun:",
                reply_markup=appeal_admin_kb(appeal_id),
            )
        except Exception:
            pass
