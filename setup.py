import os
import sys
from getpass import getpass


REQUIRED = [
    "BOT_TOKEN",
    "ADMIN",
    "HOST",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DATABASE",
]
ENV_PATH = ".env"


def load_env(path=ENV_PATH) -> dict:
    if not os.path.isfile(path):
        return {}
    data = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
    return data


def save_env(cfg: dict, path=ENV_PATH) -> None:
    with open(path, "w", encoding="utf‑8") as f:
        for k in REQUIRED:
            f.write(f"{k}={cfg[k]}\n")
    print(f"✅  {path} written.")


def prompt_for(keys: list[str], base: dict | None = None) -> dict:
    cfg = base.copy() if base else {}
    for k in keys:
        if k in cfg and cfg[k]:
            continue
        if k == "MYSQL_PASSWORD":
            val = getpass(f"{k}: ")
        else:
            val = input(f"{k}: ")
        cfg[k] = val.strip()
    return cfg


def test_mysql(cfg: dict) -> bool:
    """Attempt to connect to MySQL with the supplied settings."""
    try:
        import mysql.connector
    except ModuleNotFoundError:
        print("❌ mysql‑connector‑python not installed.  Run:\n"
              "   pip install mysql‑connector‑python")
        return False

    try:
        conn = mysql.connector.connect(
            host=cfg["HOST"],
            user=cfg["MYSQL_USER"],
            password=cfg["MYSQL_PASSWORD"],
            database=cfg["MYSQL_DATABASE"],
            connection_timeout=5,
        )
        conn.close()
        print("✅  Database connection successful.")
        return True
    except mysql.connector.Error as e:
        print(f"❌  Database connection failed: {e}")
        return False


def ask_yes(question: str, default_no=True) -> bool:
    suffix = "[y/N]: " if default_no else "[Y/n]: "
    ans = input(question + " " + suffix).strip().lower()
    return ans == "y" if default_no else ans != "n"


def main_setup() -> None:
    cfg = load_env()
    print("🔧  Configuration wizard")

    while True:
        missing = [k for k in REQUIRED if k not in cfg or not cfg[k]]
        if missing:
            print(f"Missing values: {', '.join(missing)}")
            cfg = prompt_for(missing, cfg)

        if test_mysql(cfg):
            save_env(cfg)
            break
        else:
            if not ask_yes("Re‑enter all values and try again?"):
                print("👋  Aborted. .env NOT saved.")
                break
            cfg = prompt_for(REQUIRED, {})

    print("🔧  Configuration complete.")

    from loader import FM

    
    FEATURES = ['translator', 'middlewares', 'save_log']
    for feature in FEATURES:
        FM.feature(feature)
    print("🔧  Features loaded.")


if __name__ == "__main__":
    try:
        main_setup()
    except KeyboardInterrupt:
        print("\n👋  Interrupted. .env NOT saved.")
        sys.exit(1)
