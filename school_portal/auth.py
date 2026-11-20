"""Local account storage for School Portal (SQLite + salted PBKDF2 hashes)."""

import hashlib
import hmac
import os
import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "portal.db"
PBKDF2_ROUNDS = 200_000
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


class AuthError(Exception):
    """Raised with a message that is safe to show to the user."""


def _connect(db_path=None) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                role        TEXT NOT NULL CHECK (role IN ('student', 'teacher')),
                full_name   TEXT NOT NULL,
                school_id   TEXT NOT NULL,
                grp         TEXT NOT NULL,
                email       TEXT NOT NULL,
                salt        BLOB NOT NULL,
                pw_hash     BLOB NOT NULL,
                created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (role, email),
                UNIQUE (role, school_id)
            )
            """
        )


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email))


def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS)


def register(role, full_name, school_id, group, email, password, db_path=None) -> None:
    email = email.strip().lower()
    salt = os.urandom(16)
    try:
        with _connect(db_path) as conn:
            conn.execute(
                "INSERT INTO users (role, full_name, school_id, grp, email, salt, pw_hash) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (role, full_name.strip(), school_id.strip(), group, email, salt,
                 _hash_password(password, salt)),
            )
    except sqlite3.IntegrityError as exc:
        if "email" in str(exc):
            raise AuthError("An account with this email already exists.") from exc
        raise AuthError("This ID is already registered.") from exc


def authenticate(role, email, password, db_path=None) -> dict:
    email = email.strip().lower()
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE role = ? AND email = ?", (role, email)
        ).fetchone()

    # Same message for unknown email and wrong password.
    if row is None or not hmac.compare_digest(
        _hash_password(password, row["salt"]), row["pw_hash"]
    ):
        raise AuthError("Incorrect email or password.")

    return {
        "id": row["id"],
        "role": row["role"],
        "full_name": row["full_name"],
        "school_id": row["school_id"],
        "group": row["grp"],
        "email": row["email"],
    }
