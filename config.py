"""
AFDrive configuration.

All configurable values are read from environment variables (or a local
.env file, loaded via python-dotenv). Nothing sensitive is hardcoded.
"""

import os
import secrets

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)


def _get_or_create_secret_key():
    """
    Return AFDRIVE_SECRET_KEY from the environment if set. Otherwise,
    generate a random key once and persist it to instance/secret_key.txt
    so Flask sessions survive server restarts even if the operator never
    set a secret key manually.
    """
    env_key = os.environ.get("AFDRIVE_SECRET_KEY")
    if env_key:
        return env_key

    key_file = os.path.join(INSTANCE_DIR, "secret_key.txt")
    if os.path.exists(key_file):
        with open(key_file, "r", encoding="utf-8") as f:
            existing = f.read().strip()
            if existing:
                return existing

    new_key = secrets.token_hex(32)
    # Restrict permissions best-effort (no-op on some filesystems, e.g. Termux/FAT)
    fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(new_key)
    return new_key


class Config:
    # Where uploaded files actually live on disk. Kept outside the Flask
    # source/templates/static directories by default.
    STORAGE_PATH = os.path.abspath(
        os.environ.get("AFDRIVE_STORAGE_PATH", os.path.join(BASE_DIR, "storage", "user_files"))
    )

    DATABASE_PATH = os.path.abspath(
        os.environ.get("AFDRIVE_DATABASE_PATH", os.path.join(BASE_DIR, "database.db"))
    )

    # Default 2 GB max upload size; override with AFDRIVE_MAX_UPLOAD_SIZE (bytes).
    MAX_UPLOAD_SIZE = int(os.environ.get("AFDRIVE_MAX_UPLOAD_SIZE", 2 * 1024 * 1024 * 1024))

    # Initial account. Password is only consumed the first time the database
    # is initialized (i.e. when no user exists yet). Change it afterwards
    # from the account settings, or by deleting the user row and restarting
    # with a new AFDRIVE_PASSWORD.
    USERNAME = os.environ.get("AFDRIVE_USERNAME", "admin")
    PASSWORD = os.environ.get("AFDRIVE_PASSWORD", "changeme123")

    SECRET_KEY = _get_or_create_secret_key()

    HOST = os.environ.get("AFDRIVE_HOST", "0.0.0.0")
    PORT = int(os.environ.get("AFDRIVE_PORT", 5000))
    DEBUG = os.environ.get("AFDRIVE_DEBUG", "false").strip().lower() in ("1", "true", "yes")

    # Session cookie hardening
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Only force secure cookies if explicitly running behind HTTPS/a tunnel.
    SESSION_COOKIE_SECURE = os.environ.get("AFDRIVE_FORCE_HTTPS", "false").strip().lower() in ("1", "true", "yes")

    PERMANENT_SESSION_LIFETIME_DAYS = int(os.environ.get("AFDRIVE_SESSION_DAYS", 7))


os.makedirs(Config.STORAGE_PATH, exist_ok=True)
