from __future__ import annotations

import json
import subprocess
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd
from quant_core.artifacts import write_result
from quant_core.backtest import BacktestEngine, BacktestRequest
from quant_core.data import SnapshotProvider
from quant_core.strategies import StrategyRegistry

from ..persistence.database import Database

ROOT = Path(__file__).resolve().parents[4]
WORKSPACE = ROOT / "workspace"
DB = Database(WORKSPACE / "app.db")
REGISTRY = StrategyRegistry(ROOT / "strategies")
REGISTRY.reload()
EXECUTOR = ProcessPoolExecutor(max_workers=2)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "uncommitted"


def run_backtest_job(run_id: str, request_payload: dict) -> None:
    db = Database(WORKSPACE / "app.db")
    db.execute("UPDATE runs SET status='running', updated_at=? WHERE id=?", (now(), run_id))
    try:
        registry = StrategyRegistry(ROOT / "strategies")
        registry.reload()
        request = BacktestRequest(**request_payload)
        market = SnapshotProvider(ROOT, request.snapshot_id).load(
            request.symbols, request.start, request.end, ["close"]
        )
        result = BacktestEngine(registry).run(request, market)
        commit = git_commit()
        write_result(
            result,
            WORKSPACE / "runs" / run_id,
            {"run_id": run_id, "git_commit": commit, "data_hash": market.sha256},
        )
        db.execute(
            "UPDATE runs SET status='completed',updated_at=?,git_commit=?,data_hash=? WHERE id=?",
            (now(), commit, market.sha256, run_id),
        )
    except Exception as exc:
        db.execute(
            "UPDATE runs SET status='failed',updated_at=?,error=? WHERE id=?",
            (now(), str(exc), run_id),
        )


def submit_backtest(payload: dict) -> str:
    run_id = f"run-{uuid4().hex[:12]}"
    timestamp = now()
    DB.execute(
        "INSERT INTO runs(id,status,request_json,created_at,updated_at) VALUES(?,?,?,?,?)",
        (run_id, "queued", json.dumps(payload), timestamp, timestamp),
    )
    EXECUTOR.submit(run_backtest_job, run_id, payload)
    return run_id


def get_result(run_id: str) -> dict:
    path = WORKSPACE / "runs" / run_id
    payload = json.loads((path / "result.json").read_text(encoding="utf-8"))
    payload["equity"] = pd.read_csv(path / "equity.csv").to_dict(orient="records")
    payload["trades"] = pd.read_csv(path / "trades.csv").fillna("").to_dict(orient="records")
    return payload
