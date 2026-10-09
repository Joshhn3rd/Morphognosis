"""
Database access for Morphognosis.

- If DATABASE_URL is set (Postgres, e.g. Supabase / Neon / Vercel Postgres),
  that database is used. This is what you need on Vercel, because Vercel does
  not keep files between requests.
- Otherwise a local SQLite file (instance/morphognosis.db) is used. This is
  for running the site on your own computer only.

On Vercel without DATABASE_URL the app refuses to store accounts or
measurements instead of silently losing them.
"""

import os
import sqlite3
from datetime import datetime, timezone

from flask import g


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ON_VERCEL = bool(os.getenv("VERCEL"))


class DatabaseNotConfigured(RuntimeError):
    pass


def database_url():
    return os.getenv("DATABASE_URL", "").strip()


def using_postgres():
    return database_url().startswith(("postgres://", "postgresql://"))


def sqlite_path():
    return os.getenv(
        "SQLITE_PATH",
        os.path.join(BASE_DIR, "instance", "morphognosis.db"),
    )


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def integrity_errors():
    errors = [sqlite3.IntegrityError]
    try:
        import psycopg2
        errors.append(psycopg2.IntegrityError)
    except ImportError:
        pass
    return tuple(errors)


class Database:
    """Tiny wrapper so the same SQL works on SQLite and Postgres."""

    def __init__(self, conn, postgres):
        self.conn = conn
        self.postgres = postgres

    def _sql(self, sql):
        return sql.replace("?", "%s") if self.postgres else sql

    def execute(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(self._sql(sql), params)
        return cur

    def all(self, sql, params=()):
        cur = self.execute(sql, params)
        columns = [d[0] for d in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

    def one(self, sql, params=()):
        rows = self.all(sql, params)
        return rows[0] if rows else None

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


_schema_ready = set()


def _schema(postgres):
    pk = "SERIAL PRIMARY KEY" if postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
    return [
        f"""CREATE TABLE IF NOT EXISTS users (
            id {pk},
            username TEXT NOT NULL,
            username_key TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""",
        f"""CREATE TABLE IF NOT EXISTS daily_logs (
            id {pk},
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            week INTEGER NOT NULL,
            day INTEGER NOT NULL,
            height DOUBLE PRECISION NOT NULL,
            leaves INTEGER NOT NULL,
            branches INTEGER NOT NULL,
            temperature DOUBLE PRECISION NOT NULL,
            sunlight DOUBLE PRECISION NOT NULL,
            water DOUBLE PRECISION NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE (user_id, week, day)
        )""",
        f"""CREATE TABLE IF NOT EXISTS predictions (
            id {pk},
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TEXT NOT NULL,
            payload TEXT NOT NULL
        )""",
    ]


def _connect():
    if using_postgres():
        try:
            import psycopg2
        except ImportError as exc:
            raise DatabaseNotConfigured(
                "psycopg2-binary is not installed. Run: pip install -r requirements.txt"
            ) from exc
        conn = psycopg2.connect(database_url(), connect_timeout=10)
        return Database(conn, postgres=True)

    if ON_VERCEL:
        raise DatabaseNotConfigured(
            "DATABASE_URL is not set. Add your Postgres connection string "
            "to the Vercel environment variables."
        )

    path = sqlite_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return Database(conn, postgres=False)


def get_db():
    if "db" not in g:
        db = _connect()
        key = (db.postgres, database_url() or sqlite_path())
        if key not in _schema_ready:
            for statement in _schema(db.postgres):
                db.execute(statement)
            db.commit()
            _schema_ready.add(key)
        g.db = db
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
