from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from .config import settings


DEFAULT_ROLES = {
    "buyer": "Default public buyer role.",
    "jeweler": "Professional jeweler role.",
    "designer": "Jewelry designer role.",
    "gemologist": "Gemological expert role.",
    "partner": "B2B partner role.",
    "admin": "Internal administrator role.",
    "support": "Internal support role.",
}

DEFAULT_PLANS = {
    "free": ("Free", 0, "RUB"),
    "single_report": ("Single Report", 9900, "RUB"),
    "pro": ("Professional", 49900, "RUB"),
    "partner": ("Partner", 149900, "RUB"),
}


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _db_path() -> Path:
    path = Path(settings.local_db_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with db_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                plan TEXT NOT NULL DEFAULT 'free',
                is_email_verified INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS roles (
                id TEXT PRIMARY KEY,
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_roles (
                user_id TEXT NOT NULL,
                role_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price_minor INTEGER NOT NULL,
                currency TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                guest_email TEXT,
                plan_id TEXT,
                provider TEXT NOT NULL,
                status TEXT NOT NULL,
                amount_minor INTEGER NOT NULL,
                currency TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        for role_id, description in DEFAULT_ROLES.items():
            conn.execute(
                "INSERT OR IGNORE INTO roles (id, description) VALUES (?, ?)",
                (role_id, description),
            )
        for plan_id, (name, price_minor, currency) in DEFAULT_PLANS.items():
            conn.execute(
                "INSERT OR IGNORE INTO plans (id, name, price_minor, currency) VALUES (?, ?, ?, ?)",
                (plan_id, name, price_minor, currency),
            )


def row_to_user(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    user = dict(row)
    user["roles"] = get_user_roles(user["id"])
    return user


def get_user_roles(user_id: str) -> list[str]:
    with db_connection() as conn:
        rows = conn.execute(
            "SELECT role_id FROM user_roles WHERE user_id = ? ORDER BY role_id",
            (user_id,),
        ).fetchall()
    return [row["role_id"] for row in rows]


def get_user_by_email(email: str) -> dict[str, Any] | None:
    normalized = email.strip().lower()
    with db_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (normalized,)).fetchone()
    return row_to_user(row)


def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    with db_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return row_to_user(row)


def create_user(email: str, password_hash: str, roles: list[str] | None = None, plan: str = "free") -> dict[str, Any]:
    normalized = email.strip().lower()
    now = utcnow_iso()
    user_id = str(uuid4())
    safe_roles = roles or ["buyer"]
    with db_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (id, email, password_hash, status, plan, is_email_verified, created_at, updated_at)
            VALUES (?, ?, ?, 'active', ?, 0, ?, ?)
            """,
            (user_id, normalized, password_hash, plan, now, now),
        )
        for role_id in safe_roles:
            conn.execute(
                "INSERT OR IGNORE INTO user_roles (user_id, role_id, created_at) VALUES (?, ?, ?)",
                (user_id, role_id, now),
            )
    user = get_user_by_id(user_id)
    if user is None:
        raise RuntimeError("User creation failed")
    return user


def list_plans() -> list[dict[str, Any]]:
    with db_connection() as conn:
        rows = conn.execute("SELECT * FROM plans WHERE is_active = 1 ORDER BY price_minor").fetchall()
    return [dict(row) for row in rows]


def get_plan(plan_id: str) -> dict[str, Any] | None:
    with db_connection() as conn:
        row = conn.execute("SELECT * FROM plans WHERE id = ? AND is_active = 1", (plan_id,)).fetchone()
    return dict(row) if row else None


def create_payment_contract(plan_id: str, guest_email: str | None, user_id: str | None) -> dict[str, Any]:
    plan = get_plan(plan_id)
    if plan is None:
        raise ValueError("Unknown plan")
    now = utcnow_iso()
    payment_id = str(uuid4())
    with db_connection() as conn:
        conn.execute(
            """
            INSERT INTO payments (id, user_id, guest_email, plan_id, provider, status, amount_minor, currency, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'not_connected', 'created', ?, ?, ?, ?)
            """,
            (payment_id, user_id, guest_email, plan_id, plan["price_minor"], plan["currency"], now, now),
        )
    return {
        "id": payment_id,
        "plan_id": plan_id,
        "status": "created",
        "provider": "not_connected",
        "amount_minor": plan["price_minor"],
        "currency": plan["currency"],
        "message": "Payment provider is not connected in MVP. This is a server-side contract only.",
    }


def get_payment(payment_id: str) -> dict[str, Any] | None:
    with db_connection() as conn:
        row = conn.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()
    return dict(row) if row else None
