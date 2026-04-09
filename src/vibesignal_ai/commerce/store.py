"""SQLite-backed persistence for anonymous app users, usage, and purchases."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .models import AppUserRecord, PurchaseRecord


class CommerceStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS app_users (
                    app_user_id TEXT PRIMARY KEY,
                    device_installation_id TEXT NOT NULL UNIQUE,
                    platform TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS usage_events (
                    analysis_id TEXT PRIMARY KEY,
                    app_user_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY(app_user_id) REFERENCES app_users(app_user_id)
                );

                CREATE TABLE IF NOT EXISTS purchases (
                    purchase_id TEXT PRIMARY KEY,
                    app_user_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    verification_state TEXT NOT NULL,
                    purchase_token_hash TEXT NOT NULL,
                    transaction_id TEXT NOT NULL,
                    original_transaction_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    last_verified_at TEXT NOT NULL,
                    verification_message TEXT NOT NULL,
                    FOREIGN KEY(app_user_id) REFERENCES app_users(app_user_id)
                );
                """
            )

    def get_app_user_by_device(self, device_installation_id: str) -> AppUserRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT app_user_id, device_installation_id, platform, created_at
                FROM app_users
                WHERE device_installation_id = ?
                """,
                (device_installation_id,),
            ).fetchone()
        if row is None:
            return None
        return AppUserRecord(**dict(row))

    def get_app_user(self, app_user_id: str) -> AppUserRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT app_user_id, device_installation_id, platform, created_at
                FROM app_users
                WHERE app_user_id = ?
                """,
                (app_user_id,),
            ).fetchone()
        if row is None:
            return None
        return AppUserRecord(**dict(row))

    def insert_app_user(self, user: AppUserRecord) -> AppUserRecord:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO app_users (app_user_id, device_installation_id, platform, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user.app_user_id, user.device_installation_id, user.platform, user.created_at),
            )
        return user

    def record_completed_analysis(
        self,
        *,
        app_user_id: str,
        analysis_id: str,
        conversation_id: str,
        completed_at: str,
    ) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO usage_events (
                    analysis_id, app_user_id, conversation_id, completed_at, status
                )
                VALUES (?, ?, ?, ?, 'completed')
                """,
                (analysis_id, app_user_id, conversation_id, completed_at),
            )
        return bool(cursor.rowcount)

    def count_completed_analyses(self, app_user_id: str) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS completed_count
                FROM usage_events
                WHERE app_user_id = ? AND status = 'completed'
                """,
                (app_user_id,),
            ).fetchone()
        return int(row["completed_count"] if row else 0)

    def upsert_purchase(self, purchase: PurchaseRecord) -> PurchaseRecord:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO purchases (
                    purchase_id,
                    app_user_id,
                    platform,
                    product_id,
                    verification_state,
                    purchase_token_hash,
                    transaction_id,
                    original_transaction_id,
                    expires_at,
                    started_at,
                    last_verified_at,
                    verification_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(purchase_id) DO UPDATE SET
                    app_user_id = excluded.app_user_id,
                    platform = excluded.platform,
                    product_id = excluded.product_id,
                    verification_state = excluded.verification_state,
                    purchase_token_hash = excluded.purchase_token_hash,
                    transaction_id = excluded.transaction_id,
                    original_transaction_id = excluded.original_transaction_id,
                    expires_at = excluded.expires_at,
                    started_at = excluded.started_at,
                    last_verified_at = excluded.last_verified_at,
                    verification_message = excluded.verification_message
                """,
                (
                    purchase.purchase_id,
                    purchase.app_user_id,
                    purchase.platform,
                    purchase.product_id,
                    purchase.verification_state,
                    purchase.purchase_token_hash,
                    purchase.transaction_id,
                    purchase.original_transaction_id,
                    purchase.expires_at,
                    purchase.started_at,
                    purchase.last_verified_at,
                    purchase.verification_message,
                ),
            )
        return purchase

    def list_purchases(self, app_user_id: str) -> list[PurchaseRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    app_user_id,
                    platform,
                    product_id,
                    purchase_id,
                    verification_state,
                    purchase_token_hash,
                    transaction_id,
                    original_transaction_id,
                    expires_at,
                    started_at,
                    last_verified_at,
                    verification_message
                FROM purchases
                WHERE app_user_id = ?
                ORDER BY last_verified_at DESC, purchase_id DESC
                """,
                (app_user_id,),
            ).fetchall()
        return [PurchaseRecord(**dict(row)) for row in rows]

    def replace_purchases(self, app_user_id: str, purchases: Iterable[PurchaseRecord]) -> list[PurchaseRecord]:
        normalized = list(purchases)
        with self._connect() as connection:
            connection.execute("DELETE FROM purchases WHERE app_user_id = ?", (app_user_id,))
        for purchase in normalized:
            self.upsert_purchase(purchase)
        return normalized
