from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from .config import settings


DEFAULT_ROLES = {
    "guest": "Unauthenticated visitor",
    "buyer": "Registered buyer",
    "jeweler": "Jeweler / retail professional",
    "designer": "Jewelry designer",
    "gemologist": "Gemologist / expert",
    "partner": "B2B partner",
    "support": "Support operator",
    "admin": "Internal administrator",
}

DEFAULT_PLANS = [
    ("free", "Free", 0, "RUB", ["public_catalog", "limited_score_preview"]),
    ("single_report", "Single Report", 9900, "RUB", ["single_report"]),
    ("pro", "Professional", 49900, "RUB", ["single_report", "professional_analytics", "workspace"]),
    ("partner", "Partner", 149900, "RUB", ["professional_analytics", "workspace", "partner_pricing"]),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sqlite_path_from_url(database_url: str) -> Path:
    if not database_url.startswith("sqlite:///"):
        raise RuntimeError(
            "Auth MVP V1 supports sqlite:/// database_url for local development. "
            "PostgreSQL integration remains in database/schema_postgres.sql."
        )

    raw_path = database_url.removeprefix("sqlite:///")
    path = Path(raw_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def get_db_path() -> Path:
    return sqlite_path_from_url(settings.database_url)


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    """Create local SQLite tables and seed roles/plans.

    This is a local MVP database. Production should use the PostgreSQL contract
    from database/schema_postgres.sql or a managed auth provider.
    """

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                plan TEXT NOT NULL DEFAULT 'free',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS roles (
                id TEXT PRIMARY KEY,
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_roles (
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role_id TEXT NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_id, role_id)
            );

            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price_minor INTEGER NOT NULL DEFAULT 0,
                currency TEXT NOT NULL DEFAULT 'RUB',
                features_json TEXT NOT NULL DEFAULT '[]',
                is_active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
                guest_email TEXT,
                plan_id TEXT NOT NULL REFERENCES plans(id) ON DELETE RESTRICT,
                provider TEXT NOT NULL,
                status TEXT NOT NULL,
                amount_minor INTEGER NOT NULL,
                currency TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS workspace_collections (
                id TEXT PRIMARY KEY,
                owner_user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                client_name TEXT,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS admin_audit_logs (
                id TEXT PRIMARY KEY,
                actor_user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
                action TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT,
                before_payload TEXT,
                after_payload TEXT,
                created_at TEXT NOT NULL
            );
            """
        )

        for role_id, description in DEFAULT_ROLES.items():
            db.execute(
                "INSERT OR IGNORE INTO roles (id, description) VALUES (?, ?)",
                (role_id, description),
            )

        for plan_id, name, price_minor, currency, features in DEFAULT_PLANS:
            db.execute(
                """
                INSERT OR IGNORE INTO plans (id, name, price_minor, currency, features_json, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (plan_id, name, price_minor, currency, json.dumps(features)),
            )


def row_to_user(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "email": row["email"],
        "status": row["status"],
        "plan": row["plan"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def get_user_roles(user_id: str) -> List[str]:
    with connect() as db:
        rows = db.execute(
            "SELECT role_id FROM user_roles WHERE user_id = ? ORDER BY role_id",
            (user_id,),
        ).fetchall()
    return [row["role_id"] for row in rows]


def attach_roles(user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if user is None:
        return None
    return {**user, "roles": get_user_roles(user["id"])}


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    normalized = email.strip().lower()
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE email = ?", (normalized,)).fetchone()
    return attach_roles(row_to_user(row)) if row else None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return attach_roles(row_to_user(row)) if row else None


def get_password_hash_by_email(email: str) -> Optional[str]:
    normalized = email.strip().lower()
    with connect() as db:
        row = db.execute("SELECT password_hash FROM users WHERE email = ?", (normalized,)).fetchone()
    return row["password_hash"] if row else None


def create_user(email: str, password_hash: str, requested_role: str = "buyer") -> Dict[str, Any]:
    normalized = email.strip().lower()
    requested_role = requested_role.strip().lower() or "buyer"
    allowed_self_roles = {"buyer", "jeweler", "designer", "gemologist", "partner"}

    if requested_role not in allowed_self_roles:
        raise ValueError("requested_role_not_allowed")

    user_id = str(uuid.uuid4())
    timestamp = now_iso()
    roles = {"buyer", requested_role}

    with connect() as db:
        try:
            db.execute(
                """
                INSERT INTO users (id, email, password_hash, status, plan, created_at, updated_at)
                VALUES (?, ?, ?, 'active', 'free', ?, ?)
                """,
                (user_id, normalized, password_hash, timestamp, timestamp),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("email_already_registered") from exc

        for role_id in sorted(roles):
            db.execute(
                "INSERT INTO user_roles (user_id, role_id, created_at) VALUES (?, ?, ?)",
                (user_id, role_id, timestamp),
            )

    user = get_user_by_id(user_id)
    if user is None:
        raise RuntimeError("user_creation_failed")
    return user


def public_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": user["id"],
        "email": user["email"],
        "roles": list(user.get("roles", [])),
        "plan": user.get("plan", "free"),
        "status": user.get("status", "active"),
    }


def list_plans() -> List[Dict[str, Any]]:
    with connect() as db:
        rows = db.execute(
            "SELECT id, name, price_minor, currency, features_json FROM plans WHERE is_active = 1 ORDER BY price_minor"
        ).fetchall()

    return [
        {
            "id": row["id"],
            "name": row["name"],
            "price_minor": row["price_minor"],
            "currency": row["currency"],
            "features": json.loads(row["features_json"] or "[]"),
        }
        for row in rows
    ]


def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    plans = list_plans()
    return next((plan for plan in plans if plan["id"] == plan_id), None)


def create_payment(plan_id: str, guest_email: Optional[str], user_id: Optional[str]) -> Dict[str, Any]:
    plan = get_plan(plan_id)
    if plan is None:
        raise ValueError("plan_not_found")

    payment_id = str(uuid.uuid4())
    timestamp = now_iso()

    with connect() as db:
        db.execute(
            """
            INSERT INTO payments (id, user_id, guest_email, plan_id, provider, status, amount_minor, currency, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'contract_only', 'created', ?, ?, ?, ?)
            """,
            (
                payment_id,
                user_id,
                guest_email.strip().lower() if guest_email else None,
                plan_id,
                plan["price_minor"],
                plan["currency"],
                timestamp,
                timestamp,
            ),
        )

    return get_payment(payment_id)  # type: ignore[return-value]


def get_payment(payment_id: str) -> Optional[Dict[str, Any]]:
    with connect() as db:
        row = db.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()

    if not row:
        return None

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "guest_email": row["guest_email"],
        "plan_id": row["plan_id"],
        "provider": row["provider"],
        "status": row["status"],
        "amount_minor": row["amount_minor"],
        "currency": row["currency"],
    }


def list_collections(owner_user_id: str) -> List[Dict[str, Any]]:
    with connect() as db:
        rows = db.execute(
            """
            SELECT id, owner_user_id, title, client_name, notes, status
            FROM workspace_collections
            WHERE owner_user_id = ?
            ORDER BY created_at DESC
            """,
            (owner_user_id,),
        ).fetchall()

    return [dict(row) for row in rows]


def create_collection(owner_user_id: str, title: str, client_name: Optional[str], notes: Optional[str]) -> Dict[str, Any]:
    collection_id = str(uuid.uuid4())
    timestamp = now_iso()

    with connect() as db:
        db.execute(
            """
            INSERT INTO workspace_collections (id, owner_user_id, title, client_name, notes, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'draft', ?, ?)
            """,
            (collection_id, owner_user_id, title, client_name, notes, timestamp, timestamp),
        )

    return {
        "id": collection_id,
        "owner_user_id": owner_user_id,
        "title": title,
        "client_name": client_name,
        "notes": notes,
        "status": "draft",
    }


def create_audit_log(
    actor_user_id: Optional[str],
    action: str,
    target_type: str,
    target_id: Optional[str] = None,
    before_payload: Optional[Dict[str, Any]] = None,
    after_payload: Optional[Dict[str, Any]] = None,
) -> None:
    with connect() as db:
        db.execute(
            """
            INSERT INTO admin_audit_logs (id, actor_user_id, action, target_type, target_id, before_payload, after_payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                actor_user_id,
                action,
                target_type,
                target_id,
                json.dumps(before_payload) if before_payload is not None else None,
                json.dumps(after_payload) if after_payload is not None else None,
                now_iso(),
            ),
        )


def list_audit_logs(limit: int = 50) -> List[Dict[str, Any]]:
    with connect() as db:
        rows = db.execute(
            """
            SELECT id, actor_user_id, action, target_type, target_id, created_at
            FROM admin_audit_logs
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]
