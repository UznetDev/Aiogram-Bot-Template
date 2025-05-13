import os, time, contextlib
import pytest
import mysql.connector
from redis import Redis
from pytest_docker.plugin import Services

MYSQL_URL = "mysql://root:root@localhost:3306/app_db"

# ───────────── Docker servislar tayyor bo‘lguncha kutish ─────────────
def _wait_mysql_up():
    for _ in range(20):
        try:
            mysql.connector.connect(
                host="localhost", user="root", password="root", database="app_db"
            ).close()
            return
        except mysql.connector.Error:
            time.sleep(1)
    pytest.exit("MySQL konteyneri ishga tushmadi", returncode=1)

def _wait_redis_up():
    for _ in range(20):
        try:
            Redis(host="localhost", port=6379).ping()
            return
        except Exception:
            time.sleep(1)
    pytest.exit("Redis konteyneri ishga tushmadi", returncode=1)

# ───────────── Pytest hooks ─────────────
def pytest_configure():
    os.environ["DATABASE_URL"] = MYSQL_URL
    os.environ["REDIS_HOST"] = "localhost"

# ───────────── Docker services fixture ─────────────
@pytest.fixture(scope="session", autouse=True)
def _spin_up_docker_services(docker_services: Services):
    """Redis va MySQL konteynerlarini test sessiyasi boshida ko‘taradi."""
    docker_services.start()       # docker-compose.test.yml bo‘yicha
    _wait_mysql_up()
    _wait_redis_up()
    yield
    docker_services.stop()
