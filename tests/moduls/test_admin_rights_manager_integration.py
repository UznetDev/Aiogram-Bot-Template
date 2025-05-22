# tests/test_admins_manager_int.py
import random
import pytest
import mysql.connector

from bot.loader import db, redis, AM


@pytest.mark.integration
def test_admins_manager_full_cycle():


    user_id = random.randint(10**10, 10**11 - 1)
    features = ["can_ban_users", "can_post", "is_super_admin"]

    db.cursor.execute("DELETE FROM admin_rights WHERE admin_id IN (SELECT id FROM admins WHERE user_id = %s)", (user_id,))
    db.cursor.execute("DELETE FROM admins WHERE user_id = %s", (user_id,))
    db.connection.commit()
    for f in features:
        redis.delete(AM._redis_key(user_id, f))

    AM.add(user_id)
    AM.add(user_id)

    db.cursor.execute("SELECT id FROM admins WHERE user_id=%s", (user_id,))
    admin_row = db.cursor.fetchone()
    assert admin_row, "Admin qo'shilmadi"
    admin_pk = admin_row["id"]

    for feat in features:

        assert AM.get(user_id, feat) is None

        AM.update(user_id, feat, True)

        db.cursor.execute(
            "SELECT value, is_active FROM admin_rights WHERE admin_id=%s AND name=%s",
            (admin_pk, feat),
        )
        row = db.cursor.fetchone()
        assert row and row["value"] == 1 and row["is_active"] == 1

        assert redis.get(AM._redis_key(user_id, feat)) == "1"

        assert AM.get(user_id, feat) is True

        AM.update(user_id, feat, False)

        db.cursor.execute(
            "SELECT value FROM admin_rights WHERE admin_id=%s AND name=%s",
            (admin_pk, feat),
        )
        assert db.cursor.fetchone()["value"] == 0
        assert redis.get(AM._redis_key(user_id, feat)) == "0"
        assert AM.get(user_id, feat) is False

        AM.update(user_id, feat, False, is_active=False)

        redis.delete(AM._redis_key(user_id, feat))
        assert AM.get(user_id, feat) is None

    db.cursor.execute("DELETE FROM admin_rights WHERE admin_id=%s", (admin_pk,))
    db.cursor.execute("DELETE FROM admins WHERE id=%s", (admin_pk,))
    db.connection.commit()
    for f in features:
        redis.delete(AM._redis_key(user_id, f))
