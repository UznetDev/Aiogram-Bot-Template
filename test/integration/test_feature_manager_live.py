import logging
from feature_manager import FeatureManager
from db.database import Database
from redis import Redis
import mysql.connector

log = logging.getLogger("it")

def _db():
    conn = mysql.connector.connect(
        host="localhost", user="root", password="root", database="app_db"
    )
    return Database(conn)   # sizning adapteringiz (simple wrapper bo‘lishi mumkin)

def _redis():
    return Redis(host="localhost", port=6379, decode_responses=True)

def test_live_roundtrip(tmp_path):
    fm = FeatureManager(db=_db(), redis_client=_redis(), root_logger=log)
    name = "integration_flag"

    # new → user prompt'ni bypass qilish uchun _persist chaqiramiz
    fm._persist(name, True)
    assert fm.feature(name) is True

    fm.update_feature(name, enabled=False)
    assert fm.feature(name) is False
