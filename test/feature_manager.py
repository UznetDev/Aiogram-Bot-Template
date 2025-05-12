import logging
from unittest.mock import MagicMock, patch

import pytest
from redis import RedisError

# Import the class under test
from core.feature_manager import FeatureManager


# ──────────────────────────── Fixtures ────────────────────────────

@pytest.fixture
def db_mock():
    """Return a mock of the Database adapter."""
    mock = MagicMock()
    # select_feature → None by default (no record)
    mock.select_feature.return_value = None
    # update_feature returns number of affected rows (1 = updated, 0 = not found)
    mock.update_feature.return_value = 1
    return mock


@pytest.fixture
def redis_mock():
    """Return a mock of the Redis client (decode_responses=True expected)."""
    mock = MagicMock()
    mock.hget.return_value = None  # no value cached by default
    return mock


@pytest.fixture
def logger():
    """Real logger (captures to pytest)."""
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger("feature_manager_test")


@pytest.fixture
def fm(db_mock, redis_mock, logger):
    """FeatureManager instance with mocked dependencies."""
    return FeatureManager(db=db_mock, redis_client=redis_mock, root_logger=logger)


# ──────────────────────────── Tests: Feature lookup ────────────────────────────

def test_feature_returns_cached_value(fm, redis_mock, db_mock):
    """If Redis already has the flag, it should be returned and DB not queried."""
    redis_mock.hget.return_value = "1"  # cached True
    result = fm.feature("dark_mode")
    assert result is True
    redis_mock.hget.assert_called_once_with(fm._REDIS_HASH, "dark_mode")
    # DB should be untouched
    db_mock.select_feature.assert_not_called()


def test_feature_fallbacks_to_db_and_caches(fm, redis_mock, db_mock):
    """If Redis miss but DB has value, it must be cached and returned."""
    redis_mock.hget.return_value = None
    db_mock.select_feature.return_value = 0  # False in DB

    result = fm.feature("dark_mode")
    assert result is False

    redis_mock.hset.assert_called_once_with(fm._REDIS_HASH, "dark_mode", 0)
    db_mock.select_feature.assert_called_once_with("dark_mode")


@pytest.mark.parametrize("user_input, expected_bool", [("y", True), ("n", False)])
@patch("builtins.input")
def test_feature_asks_user_when_not_found(mock_input, fm, redis_mock, db_mock, user_input, expected_bool):
    """When not in Redis nor DB, ask user; persist answer to both stores."""
    mock_input.return_value = user_input
    redis_mock.hget.return_value = None
    db_mock.select_feature.return_value = None

    result = fm.feature("beta_flag")

    assert result is expected_bool
    # Persist to DB & Redis
    db_mock.insert_feature.assert_called_once_with(name="beta_flag", enabled=expected_bool)
    redis_mock.hset.assert_called_once_with(fm._REDIS_HASH, "beta_flag", int(expected_bool))


# ──────────────────────────── Tests: update_feature ────────────────────────────

def test_update_feature_updates_existing_flag(fm, redis_mock, db_mock):
    """update_feature should call DB.update_feature and Redis.hset when flag exists."""
    db_mock.update_feature.return_value = 1  # one row updated

    fm.update_feature("dark_mode", enabled=True)

    db_mock.update_feature.assert_called_once_with(name="dark_mode", enabled=True)
    db_mock.insert_feature.assert_not_called()
    redis_mock.hset.assert_called_once_with(fm._REDIS_HASH, "dark_mode", 1)


def test_update_feature_inserts_when_not_exists(fm, redis_mock, db_mock):
    """If DB.update_feature affects 0 rows, insert_feature must be called."""
    db_mock.update_feature.return_value = 0

    fm.update_feature("new_flag", enabled=False)

    db_mock.update_feature.assert_called_once_with(name="new_flag", enabled=False)
    db_mock.insert_feature.assert_called_once_with(name="new_flag", enabled=False)
    redis_mock.hset.assert_called_once_with(fm._REDIS_HASH, "new_flag", 0)


# ──────────────────────────── Tests: error handling ────────────────────────────

def test_feature_redis_error_returns_false(fm, redis_mock, caplog):
    """If Redis raises an error, feature() should log it and return False."""
    caplog.set_level(logging.ERROR)
    redis_mock.hget.side_effect = RedisError("Redis down")

    result = fm.feature("unstable_flag")

    assert result is False
    assert any("Redis down" in r.message for r in caplog.records)


def test_update_feature_redis_error_raises(fm, redis_mock):
    """update_feature should re‑raise if RedisError occurs (transactional)."""
    redis_mock.hset.side_effect = RedisError("write failed")

    with pytest.raises(RedisError):
        fm.update_feature("any_flag", enabled=True)
