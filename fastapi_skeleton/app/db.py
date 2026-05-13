from __future__ import annotations

import hashlib
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
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

PROFESSIONAL_ROLES = {"jeweler", "designer", "gemologist", "partner"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utcnow_iso() -> str:
    return utcnow().isoformat()


def _sqlite_path_from_url(database_url: str) -> Path:
    if database_url.startswith("sqlite:///"):
        raw_path = database_url.removeprefix("sqlite:///")
        path = Path(raw_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    raise RuntimeError(
        "Auth + Workspace Hardening V1 currently supports sqlite:/// for local/private preview. "
        "PostgreSQL remains the production migration target."
    )


def _db_path() -> Path:
    return _sqlite_path_from_url(settings.database_url)


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
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

            CREATE TABLE IF NOT EXISTS role_requests (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                requested_role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                reason TEXT,
                decided_by TEXT,
                decided_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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

            CREATE TABLE IF NOT EXISTS refresh_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                refresh_token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS workspace_collections (
                id TEXT PRIMARY KEY,
                owner_user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                client_name TEXT,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS admin_audit_logs (
                id TEXT PRIMARY KEY,
                actor_user_id TEXT,
                action TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT,
                before_payload TEXT,
                after_payload TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_role_requests_user ON role_requests(user_id, status);
            CREATE INDEX IF NOT EXISTS idx_refresh_sessions_hash ON refresh_sessions(refresh_token_hash);
            CREATE INDEX IF NOT EXISTS idx_collections_owner ON workspace_collections(owner_user_id, created_at DESC);
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


def _row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def get_user_roles(user_id: str) -> list[str]:
    with db_connection() as conn:
        rows = conn.execute(
            "SELECT role_id FROM user_roles WHERE user_id = ? ORDER BY role_id",
            (user_id,),
        ).fetchall()
    return [row["role_id"] for row in rows]


def list_role_requests_for_user(user_id: str) -> list[dict[str, Any]]:
    with db_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, requested_role, status, created_at, decided_at
            FROM role_requests
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def pending_roles_for_user(user_id: str) -> list[str]:
    return [
        request["requested_role"]
        for request in list_role_requests_for_user(user_id)
        if request["status"] == "pending"
    ]


def row_to_user(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    user = dict(row)
    user["roles"] = get_user_roles(user["id"])
    user["role_requests"] = list_role_requests_for_user(user["id"])
    user["pending_roles"] = pending_roles_for_user(user["id"])
    return user


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
    safe_roles = sorted(set(roles or ["buyer"]))

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


def get_password_hash_by_email(email: str) -> str | None:
    normalized = email.strip().lower()
    with db_connection() as conn:
        row = conn.execute("SELECT password_hash FROM users WHERE email = ?", (normalized,)).fetchone()
    return row["password_hash"] if row else None


def create_role_request(user_id: str, requested_role: str, reason: str | None = None) -> dict[str, Any]:
    requested_role = requested_role.strip().lower()
    if requested_role not in PROFESSIONAL_ROLES:
        raise ValueError("unsupported_professional_role")

    existing_roles = set(get_user_roles(user_id))
    if requested_role in existing_roles:
        raise ValueError("role_already_granted")

    timestamp = utcnow_iso()
    with db_connection() as conn:
        existing = conn.execute(
            """
            SELECT * FROM role_requests
            WHERE user_id = ? AND requested_role = ? AND status IN ('pending', 'approved')
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id, requested_role),
        ).fetchone()
        if existing:
            return dict(existing)

        request_id = str(uuid4())
        conn.execute(
            """
            INSERT INTO role_requests (id, user_id, requested_role, status, reason, created_at, updated_at)
            VALUES (?, ?, ?, 'pending', ?, ?, ?)
            """,
            (request_id, user_id, requested_role, reason, timestamp, timestamp),
        )

    request = get_role_request(request_id)
    if request is None:
        raise RuntimeError("Role request creation failed")
    return request


def get_role_request(request_id: str) -> dict[str, Any] | None:
    with db_connection() as conn:
        row = conn.execute("SELECT * FROM role_requests WHERE id = ?", (request_id,)).fetchone()
    return _row_dict(row)


def list_role_requests(status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    query = """
        SELECT rr.*, u.email
        FROM role_requests rr
        JOIN users u ON u.id = rr.user_id
    """
    params: tuple[Any, ...] = ()
    if status:
        query += " WHERE rr.status = ?"
        params = (status,)
    query += " ORDER BY rr.created_at DESC LIMIT ?"
    params = (*params, limit)

    with db_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def decide_role_request(request_id: str, status: str, admin_user_id: str | None) -> dict[str, Any]:
    if status not in {"approved", "rejected"}:
        raise ValueError("unsupported_role_request_decision")

    request = get_role_request(request_id)
    if request is None:
        raise ValueError("role_request_not_found")
    if request["status"] != "pending":
        raise ValueError("role_request_not_pending")

    timestamp = utcnow_iso()
    with db_connection() as conn:
        conn.execute(
            """
            UPDATE role_requests
            SET status = ?, decided_by = ?, decided_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, admin_user_id, timestamp, timestamp, request_id),
        )
        if status == "approved":
            conn.execute(
                "INSERT OR IGNORE INTO user_roles (user_id, role_id, created_at) VALUES (?, ?, ?)",
                (request["user_id"], request["requested_role"], timestamp),
            )

    return get_role_request(request_id) or request


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


def list_collections(owner_user_id: str) -> list[dict[str, Any]]:
    with db_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, owner_user_id, title, client_name, notes, status
            FROM workspace_collections
            WHERE owner_user_id = ?
            ORDER BY created_at DESC
            """,
            (owner_user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_collection(owner_user_id: str, title: str, client_name: str | None, notes: str | None) -> dict[str, Any]:
    now = utcnow_iso()
    collection_id = str(uuid4())
    with db_connection() as conn:
        conn.execute(
            """
            INSERT INTO workspace_collections (id, owner_user_id, title, client_name, notes, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'draft', ?, ?)
            """,
            (collection_id, owner_user_id, title, client_name, notes, now, now),
        )
    return {
        "id": collection_id,
        "owner_user_id": owner_user_id,
        "title": title,
        "client_name": client_name,
        "notes": notes,
        "status": "draft",
    }


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def create_refresh_session(user_id: str, raw_token: str) -> dict[str, Any]:
    now = utcnow()
    expires = now + timedelta(days=settings.refresh_token_expire_days)
    session_id = str(uuid4())
    token_hash = _hash_refresh_token(raw_token)
    with db_connection() as conn:
        conn.execute(
            """
            INSERT INTO refresh_sessions (id, user_id, refresh_token_hash, expires_at, revoked_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, NULL, ?, ?)
            """,
            (session_id, user_id, token_hash, expires.isoformat(), now.isoformat(), now.isoformat()),
        )
    return {"id": session_id, "user_id": user_id, "expires_at": expires.isoformat()}


def get_active_refresh_session(raw_token: str) -> dict[str, Any] | None:
    token_hash = _hash_refresh_token(raw_token)
    now = utcnow()
    with db_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM refresh_sessions
            WHERE refresh_token_hash = ? AND revoked_at IS NULL
            """,
            (token_hash,),
        ).fetchone()
    session = dict(row) if row else None
    if not session:
        return None
    expires = datetime.fromisoformat(session["expires_at"])
    if expires <= now:
        revoke_refresh_session(raw_token)
        return None
    return session


def revoke_refresh_session(raw_token: str) -> None:
    token_hash = _hash_refresh_token(raw_token)
    now = utcnow_iso()
    with db_connection() as conn:
        conn.execute(
            "UPDATE refresh_sessions SET revoked_at = ?, updated_at = ? WHERE refresh_token_hash = ? AND revoked_at IS NULL",
            (now, now, token_hash),
        )


def rotate_refresh_session(raw_token: str, new_token: str) -> dict[str, Any] | None:
    session = get_active_refresh_session(raw_token)
    if not session:
        return None
    revoke_refresh_session(raw_token)
    return create_refresh_session(session["user_id"], new_token)


def create_audit_log(
    actor_user_id: str | None,
    action: str,
    target_type: str,
    target_id: str | None = None,
    before_payload: str | None = None,
    after_payload: str | None = None,
) -> None:
    now = utcnow_iso()
    with db_connection() as conn:
        conn.execute(
            """
            INSERT INTO admin_audit_logs (id, actor_user_id, action, target_type, target_id, before_payload, after_payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (str(uuid4()), actor_user_id, action, target_type, target_id, before_payload, after_payload, now),
        )


def list_audit_logs(limit: int = 100) -> list[dict[str, Any]]:
    with db_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, actor_user_id, action, target_type, target_id, created_at
            FROM admin_audit_logs
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
