import random
import pytest

from bot.loader import db  # real Database instance
from bot.data.config import ADMIN
from bot.filters.admin import SelectAdmin

# Helper functions
def _random_user_id() -> int:
    """Generate a pseudo-random Telegram-style user id."""
    return random.randint(2_000_000_000, 3_000_000_000)


def _ensure_admin_row(user_id: int):
    sql_check = "SELECT 1 FROM admins WHERE user_id = %s LIMIT 1"
    db.cursor.execute(sql_check, (user_id,))
    if not db.cursor.fetchone():
        db.insert_admin(user_id=user_id, initiator_user_id=ADMIN)

@pytest.fixture(autouse=True)
def isolation():
    # Start a transaction and roll back after each test
    db.cursor.execute("START TRANSACTION")
    yield
    db.cursor.execute("ROLLBACK")

@pytest.fixture()
def new_admin_id():
    # Create a fresh admin with all permissions = 0
    user_id = _random_user_id()
    _ensure_admin_row(user_id)
    for col in ["send_message", "statistika", "download_statistika", "block_user", "channel_settings", "add_admin"]:
        db.update_admin_data(user_id=user_id, column=col, value=0, updater_user_id=ADMIN)
    return user_id

# Tests for send_message

def test_send_message_true_for_flag(new_admin_id):
    db.update_admin_data(user_id=new_admin_id, column="send_message", value=1, updater_user_id=ADMIN)
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.send_message() is True


def test_send_message_false_for_flag(new_admin_id):
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.send_message() is False

# Tests for view_statistika

def test_view_statistika_true_for_flag(new_admin_id):
    db.update_admin_data(user_id=new_admin_id, column="statistika", value=1, updater_user_id=ADMIN)
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.view_statistika() is True


def test_view_statistika_false_for_flag(new_admin_id):
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.view_statistika() is False

# Tests for download_statistika

def test_download_statistika_true_for_flag(new_admin_id):
    db.update_admin_data(user_id=new_admin_id, column="download_statistika", value=1, updater_user_id=ADMIN)
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.download_statistika() is True


def test_download_statistika_false_for_flag(new_admin_id):
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.download_statistika() is False

# Tests for block_user

def test_block_user_true_for_flag(new_admin_id):
    db.update_admin_data(user_id=new_admin_id, column="block_user", value=1, updater_user_id=ADMIN)
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.block_user() is True


def test_block_user_false_for_flag(new_admin_id):
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.block_user() is False

# Tests for channel_settings

def test_channel_settings_true_for_flag(new_admin_id):
    db.update_admin_data(user_id=new_admin_id, column="channel_settings", value=1, updater_user_id=ADMIN)
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.channel_settings() is True


def test_channel_settings_false_for_flag(new_admin_id):
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.channel_settings() is False

# Tests for add_admin

def test_add_admin_true_for_flag(new_admin_id):
    db.update_admin_data(user_id=new_admin_id, column="add_admin", value=1, updater_user_id=ADMIN)
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.add_admin() is True


def test_add_admin_false_for_flag(new_admin_id):
    selector = SelectAdmin(user_id=new_admin_id)
    assert selector.add_admin() is False

# Tests for super admin shortcuts

def test_super_admin_methods_always_true():
    selector = SelectAdmin(user_id=ADMIN)
    assert selector.send_message() is True
    assert selector.view_statistika() is True
    assert selector.download_statistika() is True
    assert selector.block_user() is True
    assert selector.channel_settings() is True
    assert selector.add_admin() is True
