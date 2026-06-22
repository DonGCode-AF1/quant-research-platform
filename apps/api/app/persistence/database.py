from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY, status TEXT NOT NULL, request_json TEXT NOT NULL,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, error TEXT,
  git_commit TEXT, data_hash TEXT
);
CREATE TABLE IF NOT EXISTS experiments (
  id TEXT PRIMARY KEY, payload_json TEXT NOT NULL, created_at TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, sql: str, params=()):
        with self.connect() as conn:
            conn.execute(sql, params)
            conn.commit()

    def query(self, sql: str, params=()):
        with self.connect() as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def add_experiment(self, experiment_id: str, payload: dict, created_at: str):
        self.execute(
            "INSERT INTO experiments(id,payload_json,created_at) VALUES(?,?,?)",
            (experiment_id, json.dumps(payload, ensure_ascii=False), created_at),
        )
