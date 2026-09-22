import os

# --- Bot tokeni ---
# @BotFather orqali olingan tokenni shu yerga yozing (yoki BOT_TOKEN nomli environment variable orqali bering)
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

# --- Adminlar (Telegram ID lari) ---
# Telegram ID'ni bilish uchun @userinfobot ga /start yozing
SUPERADMIN_IDS = [1768033194]        # Superadmin(lar) ID(lari) - ro'yxat, bir nechta bo'lishi mumkin
DIRECTOR_ID = 222222222             # Korxona rahbari (direktor)
LAWYER_ID = 333333333               # Yurist
SECRETARY_ID = 444444444            # Sekretar

# --- Ma'lumotlar bazasi ---
DB_PATH = "database/bot.db"

# --- Direktor qabuli sozlamalari ---
WORK_START_HOUR = 8        # ish kuni boshlanishi
WORK_END_HOUR = 16         # ish kuni tugashi
LUNCH_START_HOUR = 12      # tushlik boshlanishi
LUNCH_END_HOUR = 13        # tushlik tugashi
RECEPTION_DAYS_AHEAD = 5   # nechta ish kuni (Dush-Juma) oldinga ko'rsatiladi, ertangi kundan boshlab
