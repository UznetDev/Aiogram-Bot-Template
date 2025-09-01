import pytest
from unittest.mock import patch
from bot.loader import FM, db, redis

TEST_FEATURE_NAME = "test_feature"
INITIAL_STATE = True
UPDATED_STATE = False

@pytest.fixture(autouse=True)
def setup_teardown():
    redis.hdel(FM._REDIS_HASH, TEST_FEATURE_NAME)
    db.cursor.execute("DELETE FROM `features` WHERE `name`=%s", (TEST_FEATURE_NAME,))
    db.connection.commit()
    yield
    redis.hdel(FM._REDIS_HASH, TEST_FEATURE_NAME)
    db.cursor.execute("DELETE FROM `features` WHERE `name`=%s", (TEST_FEATURE_NAME,))
    db.connection.commit()


def test_feature_manager():
    assert redis.hget(FM._REDIS_HASH, TEST_FEATURE_NAME) is None

    with patch('builtins.input', return_value='y' if INITIAL_STATE else 'n'):
        assert FM.feature(TEST_FEATURE_NAME) == INITIAL_STATE

    redis_val = redis.hget(FM._REDIS_HASH, TEST_FEATURE_NAME)
    assert bool(int(redis_val)) == INITIAL_STATE

    assert FM.feature(TEST_FEATURE_NAME) == INITIAL_STATE

    FM.upsert_feature(TEST_FEATURE_NAME, UPDATED_STATE)

    redis_updated_val = redis.hget(FM._REDIS_HASH, TEST_FEATURE_NAME)
    assert bool(int(redis_updated_val)) == UPDATED_STATE

    assert FM.feature(TEST_FEATURE_NAME) == UPDATED_STATE

    assert FM.feature(TEST_FEATURE_NAME) == UPDATED_STATE
