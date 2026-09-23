from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import DIRECTOR_ID, LAWYER_ID
from database.models import create_appeal
from keyboards.inline import appeal_admin_kb
from keyboards.reply import cancel_kb, main_menu_kb
from utils.notifications import notify_superadmins
from utils.states import CorruptionStates
from utils.warnings_text import WARNING_RU, WARNING_UZ

router = Router()


@router.message(F.text == "🔴 Korrupsiyaga guvoh bo'ldim")
async def start_corruption(message: Message, state: FSMContext):
    await message.answer(WARNING_UZ)
    await message.answer(WARNING_RU)

    await state.set_state(CorruptionStates.waiting_text)
    await message.answer(
        "Guvohi bo'lgan holatni batafsil yozib yuboring.\n"
        "Xohlasangiz rasm yoki hujjat ham biriktirishingiz mumkin.\n\n"
        "⚠️ Bu bo'limda ro'yxatdan o'tish talab qilinmaydi. "
        "Murojaatingiz korxona rahbari va yuristga yuboriladi.",
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

    # To'liq murojaat (matn/fayl + javob tugmasi) faqat korxona rahbari va yuristga boradi
    for admin_id in (DIRECTOR_ID, LAWYER_ID):
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

    # Superadminga esa har doimgidek faqat qisqa ma'lumot xabari boradi
    await notify_superadmins(
        message.bot,
        f"ℹ️ Yangi korrupsiya murojaati #{appeal_id} keldi.\n"
        f"Yuboruvchi ID: {message.from_user.id}, username: @{message.from_user.username or 'mavjud emas'}.\n"
        "To'liq matn korxona rahbari va yuristga yuborildi.",
    )
