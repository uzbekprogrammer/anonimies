from config import SUPERADMIN_IDS


async def notify_superadmins(bot, text: str):
    """Har qanday muhim harakat haqida barcha superadminlarga xabar yuboradi."""
    for admin_id in SUPERADMIN_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass
