from datetime import date as date_cls

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import DIRECTOR_ID, SECRETARY_ID
from database.models import (
    create_appointment,
    create_user,
    get_appointment,
    get_booked_slots,
    get_user,
    update_appointment_status,
)
from keyboards.inline import appointment_admin_kb, dates_kb, times_kb
from keyboards.reply import cancel_kb, main_menu_kb, phone_request_kb
from utils.notifications import notify_superadmins
from utils.states import ReceptionStates
from utils.working_days import format_date_label

router = Router()


@router.message(F.text == "📅 Direktor qabuliga yozilish")
async def start_reception(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user:
        await state.update_data(full_name=user["full_name"], phone=user["phone"])
        await state.set_state(ReceptionStates.choosing_date)
        await message.answer("Qaysi kunga yozilmoqchisiz?", reply_markup=dates_kb())
    else:
        await state.set_state(ReceptionStates.waiting_fullname)
        await message.answer("F.I.Sh ni to'liq kiriting:", reply_markup=cancel_kb())


@router.message(ReceptionStates.waiting_fullname)
async def get_fullname(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(ReceptionStates.waiting_position)
    await message.answer("Lavozimingizni kiriting:")


@router.message(ReceptionStates.waiting_position)
async def get_position(message: Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(ReceptionStates.waiting_department)
    await message.answer("Bo'lim / sexingizni kiriting:")


@router.message(ReceptionStates.waiting_department)
async def get_department(message: Message, state: FSMContext):
    await state.update_data(department=message.text)
    await state.set_state(ReceptionStates.waiting_phone)
    await message.answer(
        "Telefon raqamingizni tasdiqlash uchun tugmani bosing:",
        reply_markup=phone_request_kb(),
    )


@router.message(ReceptionStates.waiting_phone, F.contact)
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
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(ReceptionStates.choosing_date)
    await message.answer(
        "✅ Ro'yxatdan o'tdingiz.\n\nQaysi kunga yozilmoqchisiz?",
        reply_markup=dates_kb(),
    )


@router.message(ReceptionStates.waiting_phone)
async def wrong_phone(message: Message):
    await message.answer('Iltimos, "📱 Raqamni ulashish" tugmasidan foydalaning.')


@router.callback_query(ReceptionStates.choosing_date, F.data.startswith("date:"))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(":", 1)[1]
    booked = await get_booked_slots(date_str)
    await state.update_data(date=date_str)
    await state.set_state(ReceptionStates.choosing_time)

    d = date_cls.fromisoformat(date_str)
    all_slots_taken = len(booked) >= 7  # 8 soatdan tushlik chiqib 7 ta slot bor
    if all_slots_taken:
        await callback.answer("Bu kunda bo'sh vaqt qolmagan, boshqa kunni tanlang.", show_alert=True)
        return

    await callback.message.edit_text(
        f"{format_date_label(d)} kuni uchun bo'sh vaqtni tanlang:",
        reply_markup=times_kb(date_str, booked),
    )
    await callback.answer()


@router.callback_query(ReceptionStates.choosing_time, F.data.startswith("time:"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    _, date_str, time_str = callback.data.split(":", 2)
    await state.update_data(time=time_str)
    await state.set_state(ReceptionStates.waiting_reason)

    await callback.message.edit_text(f"Tanlangan vaqt: {date_str} {time_str}")
    await callback.message.answer(
        "Qabulga yozilish sababini qisqacha yozing:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(ReceptionStates.waiting_reason)
async def get_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    appointment_id = await create_appointment(
        telegram_id=message.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        reason=message.text,
        date=data["date"],
        time=data["time"],
    )
    await state.clear()

    d = date_cls.fromisoformat(data["date"])
    await message.answer(
        "✅ So'rovingiz yuborildi!\n\n"
        f"📅 Sana: {format_date_label(d)}\n"
        f"🕐 Vaqt: {data['time']}\n\n"
        "Direktor tasdiqlashi bilan sizga xabar beriladi.",
        reply_markup=main_menu_kb(),
    )

    admin_text = (
        f"📅 <b>YANGI QABULGA YOZILISH SO'ROVI</b> #{appointment_id}\n\n"
        f"F.I.Sh: {data['full_name']}\n"
        f"Telefon: {data['phone']}\n"
        f"Sana: {format_date_label(d)}\n"
        f"Vaqt: {data['time']}\n"
        f"Sabab: {message.text}"
    )
    await message.bot.send_message(DIRECTOR_ID, admin_text, reply_markup=appointment_admin_kb(appointment_id))
    await notify_superadmins(message.bot, admin_text)


@router.callback_query(F.data.startswith("confirm_appt:"))
async def confirm_appointment(callback: CallbackQuery):
    if callback.from_user.id != DIRECTOR_ID:
        await callback.answer("Bu tugma faqat direktor uchun.", show_alert=True)
        return

    appointment_id = int(callback.data.split(":")[1])
    await update_appointment_status(appointment_id, "tasdiqlandi")
    appt = await get_appointment(appointment_id)
    d = date_cls.fromisoformat(appt["appointment_date"])

    await callback.message.edit_text(callback.message.text + "\n\n✅ TASDIQLANDI")
    await callback.answer("Tasdiqlandi")

    # 1) Murojaatchiga xabar
    await callback.bot.send_message(
        appt["telegram_id"],
        f"✅ Sizning {format_date_label(d)} kuni soat {appt['appointment_time']} dagi "
        "direktor qabuliga yozilishingiz tasdiqlandi.",
    )

    # 2) Sekretarga yuboriladi
    await callback.bot.send_message(
        SECRETARY_ID,
        f"📌 Tasdiqlangan qabul #{appointment_id}\n\n"
        f"F.I.Sh: {appt['full_name']}\n"
        f"Telefon: {appt['phone']}\n"
        f"Sana: {format_date_label(d)}\n"
        f"Vaqt: {appt['appointment_time']}\n"
        f"Sabab: {appt['reason']}",
    )

    # 3) Superadminga xabar
    await notify_superadmins(
        callback.bot,
        f"ℹ️ Direktor #{appointment_id} qabulni tasdiqladi va sekretarga yubordi.",
    )


@router.callback_query(F.data.startswith("reject_appt:"))
async def reject_appointment(callback: CallbackQuery):
    if callback.from_user.id != DIRECTOR_ID:
        await callback.answer("Bu tugma faqat direktor uchun.", show_alert=True)
        return

    appointment_id = int(callback.data.split(":")[1])
    await update_appointment_status(appointment_id, "rad_etildi")
    appt = await get_appointment(appointment_id)

    await callback.message.edit_text(callback.message.text + "\n\n❌ RAD ETILDI")
    await callback.answer("Rad etildi")

    await callback.bot.send_message(
        appt["telegram_id"],
        "❌ Afsuski, so'ragan vaqtingizga direktor qabuliga yozilish rad etildi. "
        "Iltimos, boshqa vaqtga qayta murojaat qiling.",
    )

    await notify_superadmins(
        callback.bot,
        f"ℹ️ Direktor #{appointment_id} qabul so'rovini rad etdi.",
    )
