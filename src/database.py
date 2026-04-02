import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "Database", "jobs.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    return conn


def create_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = _connect()

    # Create table if it doesn't exist at all
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            prediction  TEXT,
            created_at  DATETIME DEFAULT (datetime('now'))
        )
    """)

    # ── Migration: add created_at to existing DB if the column is missing ──
    existing_columns = [
        row[1] for row in conn.execute("PRAGMA table_info(jobs)").fetchall()
    ]
    if "created_at" not in existing_columns:
        conn.execute(
            "ALTER TABLE jobs ADD COLUMN created_at DATETIME DEFAULT (datetime('now'))"
        )

    conn.commit()
    conn.close()


def insert_job(description, prediction):
    conn = _connect()
    conn.execute(
        "INSERT INTO jobs (description, prediction) VALUES (?, ?)",
        (description, prediction),
    )
    conn.commit()
    conn.close()


def get_all_jobs():
    """Return all jobs newest-first as a list of dicts."""
    conn = _connect()
    rows = conn.execute(
        "SELECT id, description, prediction, created_at FROM jobs ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats():
    """Return {total, fake, real, fake_pct} dict."""
    conn = _connect()
    total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    fake  = conn.execute("SELECT COUNT(*) FROM jobs WHERE prediction='Fake Job'").fetchone()[0]
    conn.close()
    real  = total - fake
    return {
        "total":    total,
        "fake":     fake,
        "real":     real,
        "fake_pct": round(fake / total * 100, 1) if total else 0,
    }