import random
import pytest

from bot.loader import db, redis, AM            # allaqachon tayyor obyektlar
from bot.data.config import ADMIN               # super-admin user_id

FEATURES = ["can_ban_users", "can_post", "is_super_admin"]


def r_key(user_id: int, feature: str) -> str:
    """is_active kesh kaliti."""
    return f"{AM.ns}:{user_id}:features:feature:{feature}:is_active"


def r_init_key(user_id: int, feature: str) -> str:
    """initiator_user_id kesh kaliti."""
    return f"{AM.ns}:{user_id}:features:feature:{feature}:initiator_user_id"


@pytest.mark.integration
def test_admins_manager_full_cycle():
    # --- 1. Tayyorlov ------------------------------------------------------
    user_id = random.randint(10**10, 10**11 - 1)

    # DB va Redisni tozalash (bo‘lishi mumkin bo‘lgan eski qoldiqlarni o‘chirib tashlash)
    db.cursor.execute(
        "DELETE FROM admin_rights WHERE admin_id IN (SELECT id FROM admins WHERE user_id=%s)",
        (user_id,),
    )
    db.cursor.execute("DELETE FROM admins WHERE user_id=%s", (user_id,))
    db.connection.commit()
    for key in list(redis.scan_iter(f"{AM.ns}:{user_id}*")):
        redis.delete(key)

    # --- 2. Admin qo‘shish --------------------------------------------------
    AM.add(user_id=user_id, initiator_user_id=ADMIN)

    # bazaga yozilganini tekshirish
    db.cursor.execute("SELECT id FROM admins WHERE user_id=%s", (user_id,))
    admin_row = db.cursor.fetchone()
    assert admin_row, "Admin qo'shilmadi."
    admin_pk = admin_row["id"]

    # __getitem__ keshga ham yozishini tekshiramiz
    is_admin, init_id, role = AM[user_id]
    assert (is_admin, init_id, role) == (True, ADMIN, "admin")
    assert redis.get(f"{AM.ns}:{user_id}:is_active") == "1"

    # --- 3. Har bir feature bo‘yicha sikl ----------------------------------
    for feat in FEATURES:
        # 3.1 Boshlang‘ich holat: huquq yo‘q
        assert AM(user_id, feat) is None

        # 3.2 Huquqni yoqish
        AM.update(user_id, feat, True, initiator_user_id=ADMIN)

        #  DB
        db.cursor.execute(
            "SELECT value, is_active, initiator_user_id "
            "FROM admin_rights WHERE admin_id=%s AND name=%s;",
            (admin_pk, feat),
        )
        row = db.cursor.fetchone()
        assert row and row["value"] == 1 and row["is_active"] == 1 and row["initiator_user_id"] == ADMIN

        # Redis
        assert redis.get(r_key(user_id, feat)) == "1"
        assert redis.get(r_init_key(user_id, feat)) == str(ADMIN)

        # __call__ (keshdan o‘qiydi)
        assert AM(user_id, feat) is True

        # 3.3 Huquqni o‘chirish
        AM.update(user_id, feat, False, initiator_user_id=ADMIN)
        assert AM(user_id, feat) is False
        assert redis.get(r_key(user_id, feat)) == "0"

        # 3.4 Noto‘g‘ri initiator urinishini rad etish
        wrong_initiator = random.randint(10**10, 10**11 - 1)
        AM.update(user_id, feat, True, initiator_user_id=wrong_initiator)
        # qiymat o‘zgarmasligi kerak
        assert AM(user_id, feat) is False

    # --- 4. Adminni o‘chirish ----------------------------------------------
    AM.remove(user_id, initiator_user_id=ADMIN)
    is_admin, *_ = AM[user_id]
    assert is_admin is False
    assert redis.get(f"{AM.ns}:{user_id}:is_active") == "0"

    # --- 5. Super-admin tezkor yo‘llari ------------------------------------
    # __getitem__
    sa_is_admin, sa_init, sa_role = AM[ADMIN]
    assert sa_is_admin is True and sa_role == "super_admin"

    # __call__ (huquq nomi muhim emas)
    assert AM(ADMIN, "qandaydir_huquq") is True
    status, initiator = AM(ADMIN, "another", return_intiator=True)
    assert status is True and initiator == ADMIN

    # Super-admin huquqi yangilansa ham effekt qilmasligi kerak
    AM.update(user_id=ADMIN, feature="any_feature", value=False, initiator_user_id=ADMIN)
    assert AM(ADMIN, "any_feature") is True

    # --- 6. Tozalash --------------------------------------------------------
    db.cursor.execute("DELETE FROM admin_rights WHERE admin_id=%s", (admin_pk,))
    db.cursor.execute("DELETE FROM admins WHERE id=%s", (admin_pk,))
    db.connection.commit()
    for key in list(redis.scan_iter(f"{AM.ns}:{user_id}*")):
        redis.delete(key)
