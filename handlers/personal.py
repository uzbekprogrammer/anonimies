from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import DIRECTOR_ID, LAWYER_ID
from database.models import create_appeal, create_user, get_user
from keyboards.inline import appeal_admin_kb
from keyboards.reply import cancel_kb, main_menu_kb, phone_request_kb
from utils.notifications import notify_superadmins
from utils.states import PersonalStates
from utils.warnings_text import WARNING_RU, WARNING_UZ

router = Router()


@router.message(F.text == "👤 Shaxsiy masala bo'yicha murojaat")
async def start_personal(message: Message, state: FSMContext):
    await message.answer(WARNING_UZ)
    await message.answer(WARNING_RU)

    user = await get_user(message.from_user.id)
    if user:
        await state.set_state(PersonalStates.waiting_appeal_text)
        await message.answer(
            "Shaxsiy masalangiz yuzasidan murojaatingizni yozib yuboring:",
            reply_markup=cancel_kb(),
        )
    else:
        await state.set_state(PersonalStates.waiting_fullname)
        await message.answer(
            "Bu bo'limda murojaat qilish uchun avval ro'yxatdan o'tishingiz kerak.\n\n"
            "F.I.Sh ni to'liq kiriting:",
            reply_markup=cancel_kb(),
        )


@router.message(PersonalStates.waiting_fullname)
async def get_fullname(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(PersonalStates.waiting_position)
    await message.answer("Lavozimingizni kiriting:")


@router.message(PersonalStates.waiting_position)
async def get_position(message: Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(PersonalStates.waiting_department)
    await message.answer("Bo'lim / sexingizni kiriting:")


@router.message(PersonalStates.waiting_department)
async def get_department(message: Message, state: FSMContext):
    await state.update_data(department=message.text)
    await state.set_state(PersonalStates.waiting_phone)
    await message.answer(
        "Telefon raqamingizni tasdiqlash uchun quyidagi tugmani bosing:",
        reply_markup=phone_request_kb(),
    )


@router.message(PersonalStates.waiting_phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer("Iltimos, faqat o'zingizning raqamingizni ulashing.")
        return

    data = await state.get_data()
    await create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=data["full_name"],
        position=data["position"],
        department=data["department"],
        phone=message.contact.phone_number,
    )

    await state.set_state(PersonalStates.waiting_appeal_text)
    await message.answer(
        "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz.\n\n"
        "Endi shaxsiy masalangiz yuzasidan murojaatingizni yozing:",
        reply_markup=cancel_kb(),
    )


@router.message(PersonalStates.waiting_phone)
async def wrong_phone_input(message: Message):
    await message.answer('Iltimos, pastdagi "📱 Raqamni ulashish" tugmasidan foydalaning.')


@router.message(PersonalStates.waiting_appeal_text)
async def receive_personal_appeal(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    text = message.caption or message.text or ""
    file_id, file_type = None, None
    if message.photo:
        file_id, file_type = message.photo[-1].file_id, "photo"
    elif message.document:
        file_id, file_type = message.document.file_id, "document"

    appeal_id = await create_appeal(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=user["full_name"],
        appeal_type="personal",
        text=text,
        file_id=file_id,
        file_type=file_type,
    )

    await state.clear()
    await message.answer(
        f"✅ Murojaatingiz qabul qilindi. Murojaat raqami: #{appeal_id}\n"
        "Javob kelishi bilan sizga xabar beriladi.",
        reply_markup=main_menu_kb(),
    )

    admin_text = (
        f"👤 <b>YANGI SHAXSIY MUROJAAT</b> #{appeal_id}\n\n"
        f"F.I.Sh: {user['full_name']}\n"
        f"Lavozim: {user['position']}\n"
        f"Bo'lim: {user['department']}\n"
        f"Telefon: {user['phone']}\n\n"
        f"Matn: {text or '(matn kiritilmagan)'}"
    )

    # To'liq murojaat (matn/fayl + javob tugmasi) faqat direktor va yuristga boradi
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

    # Superadminga esa faqat qisqa ma'lumot xabari boradi (to'liq matn/fayl emas)
    await notify_superadmins(
        message.bot,
        f"ℹ️ Yangi shaxsiy murojaat #{appeal_id} keldi.\n"
        f"Yuboruvchi: {user['full_name']} ({user['position']}, {user['department']})\n"
        "To'liq matn direktor va yuristga yuborildi.",
    )
