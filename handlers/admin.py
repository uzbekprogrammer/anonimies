from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.models import get_all_users, get_appeal, answer_appeal
from keyboards.inline import confirm_broadcast_kb
from utils.notifications import notify_superadmins
from utils.roles import is_admin, is_director, is_lawyer, is_superadmin
from utils.states import AdminStates

router = Router()


# ---------------------- Murojaatga javob yozish ----------------------

@router.callback_query(F.data.startswith("answer_appeal:"))
async def start_answer(callback: CallbackQuery, state: FSMContext):
    appeal_id = int(callback.data.split(":")[1])
    appeal = await get_appeal(appeal_id)
    if not appeal:
        await callback.answer("Murojaat topilmadi.", show_alert=True)
        return

    user_id = callback.from_user.id
    if appeal["appeal_type"] == "corruption" and not is_superadmin(user_id):
        await callback.answer("Bu murojaatga faqat superadmin javob bera oladi.", show_alert=True)
        return
    if appeal["appeal_type"] == "personal" and not (
        is_superadmin(user_id) or is_director(user_id) or is_lawyer(user_id)
    ):
        await callback.answer("Sizda bu murojaatga javob berish huquqi yo'q.", show_alert=True)
        return

    await state.update_data(appeal_id=appeal_id)
    await state.set_state(AdminStates.waiting_comment)
    await callback.message.answer(f"#{appeal_id} murojaatga javobingizni yozing:")
    await callback.answer()


@router.message(AdminStates.waiting_comment)
async def receive_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    appeal_id = data["appeal_id"]
    appeal = await get_appeal(appeal_id)

    role_label = "Superadmin"
    if is_director(message.from_user.id):
        role_label = "Korxona rahbari"
    elif is_lawyer(message.from_user.id):
        role_label = "Yurist"

    await answer_appeal(appeal_id, message.text, role_label)
    await state.clear()
    await message.answer(f"✅ #{appeal_id} murojaatga javobingiz yuborildi.")

    # Murojaatchiga javobni yetkazish
    try:
        await message.bot.send_message(
            appeal["telegram_id"],
            f"📩 #{appeal_id} murojaatingizga javob keldi ({role_label}):\n\n{message.text}",
        )
    except Exception:
        pass

    # Superadminga xabar
    await notify_superadmins(
        message.bot,
        f"ℹ️ {role_label} #{appeal_id} murojaatga javob yozdi:\n\n{message.text}",
    )


# ---------------------- Barchaga xabar yuborish (broadcast) ----------------------

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.waiting_broadcast)
    await message.answer("Barchaga yuboriladigan xabar matnini kiriting:")


@router.message(AdminStates.waiting_broadcast)
async def receive_broadcast_text(message: Message, state: FSMContext):
    await state.update_data(broadcast_text=message.text)
    await message.answer(
        f"Quyidagi xabar barcha foydalanuvchilarga yuborilsinmi?\n\n{message.text}",
        reply_markup=confirm_broadcast_kb(),
    )


@router.callback_query(F.data == "broadcast:send")
async def send_broadcast(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("broadcast_text")
    await state.clear()
    if not text:
        await callback.answer()
        return

    users = await get_all_users()
    sent, failed = 0, 0
    for uid in users:
        try:
            await callback.bot.send_message(uid, text)
            sent += 1
        except Exception:
            failed += 1

    await callback.message.edit_text(f"✅ Yuborildi: {sent} ta\n❌ Yuborilmadi: {failed} ta")
    await notify_superadmins(
        callback.bot,
        f"ℹ️ {callback.from_user.full_name} broadcast yubordi: {sent} ta foydalanuvchiga.",
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast:cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Bekor qilindi.")
    await callback.answer()
