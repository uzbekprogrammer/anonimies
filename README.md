# Xodimlar Murojaat Boti

Issiqlik elektr stansiyasi xodimlari uchun 3 funksiyali murojaat boti (Telegram, aiogram 3).

## Bot funksiyalari

1. **🔴 Korrupsiyaga guvoh bo'ldim** — ro'yxatdan o'tmasdan, faqat superadminga (ID va username bilan) yuboriladi.
2. **👤 Shaxsiy masala bo'yicha murojaat** — F.I.Sh, lavozim, bo'lim kiritiladi, telefon raqami Telegram "Kontakt ulashish" tugmasi orqali tasdiqlanadi, so'ng murojaat yuboriladi. Murojaat superadmin, direktor va yuristga boradi.
3. **📅 Direktor qabuliga yozilish** — ertangi kundan boshlab 1 ish haftalik (Dush-Juma) kunlar va soatlik vaqt oralig'i (8:00-16:00, 12:00-13:00 tushlik tanaffusisiz) ko'rsatiladi. Direktor tasdiqlasa — xodimga xabar boradi va so'rov sekretarga yuboriladi; rad etsa — xodimga xabar beriladi.

Har bir harakat (yangi murojaat, javob, tasdiqlash/rad etish, broadcast) haqida **barcha superadminlarga** avtomatik xabar boradi.

## O'rnatish

1. Python 3.10+ o'rnatilgan bo'lishi kerak.
2. Kerakli kutubxonalarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```
3. `config.py` faylini oching va quyidagilarni to'ldiring:
   - `BOT_TOKEN` — @BotFather dan olingan token
   - `SUPERADMIN_IDS` — superadmin(lar) Telegram ID(lari), ro'yxat: `[123456789, 987654321]`
   - `DIRECTOR_ID` — korxona rahbari Telegram ID'si
   - `LAWYER_ID` — yurist Telegram ID'si
   - `SECRETARY_ID` — sekretar Telegram ID'si

   > Telegram ID'ni bilish uchun @userinfobot ga `/start` yozing.

4. Botni ishga tushiring:
   ```bash
   python main.py
   ```

## Admin buyruqlari

- `/broadcast` — barcha ro'yxatdan o'tgan foydalanuvchilarga bir vaqtda xabar yuborish (barcha 4 admin turi uchun ochiq).
- Har bir murojaat ostida chiqadigan **"💬 Javob yozish"** tugmasi orqali xodimga javob yozish mumkin (korrupsiya murojaatlariga faqat superadmin, shaxsiy murojaatlarga superadmin/direktor/yurist javob bera oladi).

## Loyiha tuzilishi

```
xodimlar_bot/
├── main.py                  # Botni ishga tushirish nuqtasi
├── config.py                # Token va admin ID'lar
├── requirements.txt
├── database/
│   ├── db.py                 # Jadvallarni yaratish (SQLite)
│   └── models.py              # CRUD funksiyalar
├── keyboards/
│   ├── reply.py               # Oddiy klaviaturalar (menyu, bekor qilish)
│   └── inline.py               # Inline klaviaturalar (sana/vaqt, admin tugmalari)
├── handlers/
│   ├── start.py               # /start va umumiy bekor qilish
│   ├── corruption.py          # Korrupsiya bo'limi
│   ├── personal.py            # Shaxsiy masalalar bo'limi
│   ├── reception.py           # Direktor qabuliga yozilish
│   └── admin.py                # Javob yozish, broadcast
└── utils/
    ├── states.py                # FSM holatlari
    ├── roles.py                 # Admin rollarini tekshirish
    ├── working_days.py          # Ish kunlari / vaqt slotlari hisoblash
    └── notifications.py          # Superadminlarga avtomatik xabar
```

## Ma'lumotlar bazasi (SQLite, `database/bot.db`)

- **users** — ro'yxatdan o'tgan barcha xodimlar (shaxsiy masala yoki qabulga yozilish orqali)
- **appeals** — korrupsiya va shaxsiy murojaatlar, holati va admin javoblari bilan
- **appointments** — direktor qabuliga yozilish so'rovlari, holati va sana/vaqti bilan

## Keyingi qadamlar (tavsiya)

- Botni doimiy ishlaydigan serverga (VPS) joylashtirish, masalan `systemd` yoki `screen`/`tmux` orqali.
- Katta yuklamalar uchun `aiogram` FSM storage'ni `MemoryStorage` o'rniga `RedisStorage` ga o'zgartirish (bot qayta ishga tushganda holatlar saqlanib qolishi uchun).
- Admin panelga statistik hisobot (nechta murojaat, o'rtacha javob vaqti) qo'shish.
