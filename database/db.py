import aiosqlite

from config import DB_PATH


async def init_db():
    """Bot ishga tushganda barcha kerakli jadvallarni yaratadi (agar mavjud bo'lmasa)."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Ro'yxatdan o'tgan barcha foydalanuvchilar (shaxsiy masala / qabulga yozilish orqali)
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                position TEXT,
                department TEXT,
                phone TEXT,
                registered_at TEXT DEFAULT (datetime('now'))
            )
            """
        )

        # Korrupsiya va shaxsiy masalalar bo'yicha murojaatlar
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS appeals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                username TEXT,
                full_name TEXT,
                appeal_type TEXT NOT NULL,      -- 'corruption' yoki 'personal'
                text TEXT,
                file_id TEXT,
                file_type TEXT,                 -- 'photo' yoki 'document'
                status TEXT DEFAULT 'yangi',    -- yangi / javob_berildi
                admin_comment TEXT,
                answered_by TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                answered_at TEXT
            )
            """
        )

        # Direktor qabuliga yozilish so'rovlari
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                full_name TEXT,
                phone TEXT,
                reason TEXT,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT DEFAULT 'kutilmoqda',  -- kutilmoqda / tasdiqlandi / rad_etildi
                director_comment TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                decided_at TEXT
            )
            """
        )

        await db.commit()
