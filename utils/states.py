from aiogram.fsm.state import State, StatesGroup


class PersonalStates(StatesGroup):
    """Shaxsiy masalalar bo'limi uchun holatlar."""
    waiting_fullname = State()
    waiting_position = State()
    waiting_department = State()
    waiting_phone = State()
    waiting_appeal_text = State()


class CorruptionStates(StatesGroup):
    """Korrupsiyaga guvoh bo'lish bo'limi uchun holatlar."""
    waiting_text = State()


class ReceptionStates(StatesGroup):
    """Direktor qabuliga yozilish bo'limi uchun holatlar."""
    waiting_fullname = State()
    waiting_phone = State()
    choosing_date = State()
    choosing_time = State()
    waiting_reason = State()


class AdminStates(StatesGroup):
    """Admin panel uchun holatlar (javob yozish, xabar tarqatish)."""
    waiting_comment = State()
    waiting_broadcast = State()
