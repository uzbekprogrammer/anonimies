import aiosqlite

from config import DB_PATH


# ---------------------- USERS ----------------------

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def create_user(telegram_id, username, full_name, position, department, phone):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (telegram_id, username, full_name, position, department, phone)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name,
                position=excluded.position,
                department=excluded.department,
                phone=excluded.phone
            """,
            (telegram_id, username, full_name, position, department, phone),
        )
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT telegram_id FROM users")
        rows = await cur.fetchall()
        return [r["telegram_id"] for r in rows]


# ---------------------- APPEALS (korrupsiya / shaxsiy) ----------------------

async def create_appeal(telegram_id, username, full_name, appeal_type, text, file_id=None, file_type=None):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            INSERT INTO appeals (telegram_id, username, full_name, appeal_type, text, file_id, file_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (telegram_id, username, full_name, appeal_type, text, file_id, file_type),
        )
        await db.commit()
        return cur.lastrowid


async def get_appeal(appeal_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM appeals WHERE id = ?", (appeal_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def answer_appeal(appeal_id: int, comment: str, answered_by: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE appeals
            SET status='javob_berildi', admin_comment=?, answered_by=?, answered_at=datetime('now')
            WHERE id=?
            """,
            (comment, answered_by, appeal_id),
        )
        await db.commit()


# ---------------------- APPOINTMENTS (direktor qabuli) ----------------------

async def create_appointment(telegram_id, full_name, phone, reason, date, time):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            INSERT INTO appointments (telegram_id, full_name, phone, reason, appointment_date, appointment_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (telegram_id, full_name, phone, reason, date, time),
        )
        await db.commit()
        return cur.lastrowid


async def get_appointment(appointment_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_booked_slots(date: str):
    """Berilgan sana uchun band qilingan (rad etilmagan) vaqtlar ro'yxati."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT appointment_time FROM appointments WHERE appointment_date = ? AND status != 'rad_etildi'",
            (date,),
        )
        rows = await cur.fetchall()
        return [r["appointment_time"] for r in rows]


async def update_appointment_status(appointment_id: int, status: str, comment: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE appointments
            SET status=?, director_comment=?, decided_at=datetime('now')
            WHERE id=?
            """,
            (status, comment, appointment_id),
        )
        await db.commit()
