import pytest
from bot.loader import MMM, db
from bot.data.config import ADMIN

# Sample user IDs for testing
INITIATOR_ID = 123456789  # Replace with a valid user ID for testing
OTHER_USER_ID = 987654321  # A user who did not initiate the channel
CHANNEL_ID = -1001122334455  # Replace with a test Telegram channel ID


def test_manage_mandatory_membership_flow():
    # Initialize the ManageMandatoryMembership instance
    mm = MMM

    # Ensure clean state in Redis and MySQL
    redis_key = f"mandatory_membership:{CHANNEL_ID}"
    mm.redis.delete(redis_key)
    db.cursor.execute("DELETE FROM mandatory_membership WHERE channel_id = %s", (CHANNEL_ID,))
    db.connection.commit()

    # 1. Add a new channel (should succeed)
    mm.update(channel_id=CHANNEL_ID, is_active=True, updater_user_id=INITIATOR_ID)

    # Verify channel is active in Redis
    data_json = mm.redis.get(redis_key)
    assert data_json is not None, "Channel data should exist in Redis after adding"

    # Verify channel is active in MySQL
    db.cursor.execute(
        "SELECT is_active, initiator_user_id, updater_user_id FROM mandatory_membership WHERE channel_id = %s",
        (CHANNEL_ID,)
    )
    row = db.cursor.fetchone()
    assert row, "Channel row should exist in MySQL after adding"
    assert row['is_active'] == 1, "Channel should be marked active in MySQL"
    assert row['initiator_user_id'] == INITIATOR_ID, "Initiator ID should match in MySQL"

    # 2. Unauthorized update attempt (should raise PermissionError)
    with pytest.raises(PermissionError):
        mm.update(channel_id=CHANNEL_ID, is_active=False, updater_user_id=OTHER_USER_ID)

    # 3. Authorized update by super admin (should succeed)
    mm.update(channel_id=CHANNEL_ID, is_active=False, updater_user_id=ADMIN)
    # # Verify status updated in Redis
    # data_json = mm.redis.get(redis_key)
    # assert b"\"is_active\": false" in data_json, "Redis should reflect inactive status"
    # Verify status updated in MySQL
    db.cursor.execute(
        "SELECT is_active FROM mandatory_membership WHERE channel_id = %s",
        (CHANNEL_ID,)
    )
    updated_row = db.cursor.fetchone()
    assert updated_row['is_active'] == 0, "Channel should be marked inactive in MySQL"

    # 4. channels() should list only active channels (none in this case)
    active_channels = mm.channels()
    assert CHANNEL_ID not in active_channels, "Inactive channel should not be returned by channels()"
