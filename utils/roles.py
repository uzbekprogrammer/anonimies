from config import SUPERADMIN_IDS, DIRECTOR_ID, LAWYER_ID, SECRETARY_ID


def is_superadmin(user_id: int) -> bool:
    return user_id in SUPERADMIN_IDS


def is_director(user_id: int) -> bool:
    return user_id == DIRECTOR_ID


def is_lawyer(user_id: int) -> bool:
    return user_id == LAWYER_ID


def is_secretary(user_id: int) -> bool:
    return user_id == SECRETARY_ID


def is_admin(user_id: int) -> bool:
    """Superadmin, direktor, yurist yoki sekretarmi - istalgan admin turi."""
    return (
        is_superadmin(user_id)
        or is_director(user_id)
        or is_lawyer(user_id)
        or is_secretary(user_id)
    )
