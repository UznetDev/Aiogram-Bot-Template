import pytest
from bot.loader import SM, db, redis

TEST_KEY = "test_setting_key"
INITIAL_VALUE = "initial_test_value"
UPDATED_VALUE = "updated_test_value"

@pytest.fixture(autouse=True)
def setup_teardown():
    redis.hdel(SM._REDIS_HASH, TEST_KEY)
    db.cursor.execute("DELETE FROM settings WHERE `key`=%s", (TEST_KEY,))
    db.connection.commit()
    yield
    redis.hdel(SM._REDIS_HASH, TEST_KEY)
    db.cursor.execute("DELETE FROM settings WHERE `key`=%s", (TEST_KEY,))
    db.connection.commit()

def test_settings_manager_get_and_update():
    assert SM.get(TEST_KEY) is None

    SM.upsert(TEST_KEY, INITIAL_VALUE, user_id=12345)

    redis_val = redis.hget(SM._REDIS_HASH, TEST_KEY)
    assert redis_val == INITIAL_VALUE

    assert SM.get(TEST_KEY) == INITIAL_VALUE

    SM.upsert(TEST_KEY, UPDATED_VALUE, user_id=54321)

    redis_updated_val = redis.hget(SM._REDIS_HASH, TEST_KEY)
    assert redis_updated_val == UPDATED_VALUE


    assert SM.get(TEST_KEY) == UPDATED_VALUE
