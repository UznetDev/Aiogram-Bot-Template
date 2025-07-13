import pytest

from bot.loader import MMM, db, redis
from bot.data.config import ADMIN

TEST_CHANNEL = 999999999

@pytest.fixture(autouse=True)
def cleanup():
    redis.delete(f"{MMM._REDIS_HASH}:{TEST_CHANNEL}")
    redis.delete(f"{MMM._REDIS_HASH}:all")
    db.cursor.execute("DELETE FROM channels WHERE channel_id=%s", (TEST_CHANNEL,))
    db.connection.commit()
    yield
    redis.delete(f"{MMM._REDIS_HASH}:{TEST_CHANNEL}")
    redis.delete(f"{MMM._REDIS_HASH}:all")
    db.cursor.execute("DELETE FROM channels WHERE channel_id=%s", (TEST_CHANNEL,))
    db.connection.commit()


def test_update_and_channels():
    MMM.update(TEST_CHANNEL, True, ADMIN)
    assert redis.get(f"{MMM._REDIS_HASH}:{TEST_CHANNEL}") is not None
    channels = MMM.channels()
    assert TEST_CHANNEL in channels

