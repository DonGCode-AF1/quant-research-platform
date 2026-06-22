from __future__ import annotations

import json
from datetime import datetime, timezone

import yaml
from fastapi import APIRouter, HTTPException

from ..schemas.models import BacktestCreate, ComparisonCreate, ExperimentCreate
from ..services.runtime import DB, REGISTRY, ROOT, get_result, submit_backtest

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {"status": "ok", "strategies": len(REGISTRY.items)}


@router.get("/strategies")
def strategies():
    return REGISTRY.list()


@router.get("/strategies/{strategy_id}")
def strategy(strategy_id: str):
    try:
        return REGISTRY.get(strategy_id).metadata
    except KeyError as exc:
        raise HTTPException(404, "Strategy not found") from exc


@router.post("/strategies/reload")
def reload_strategies():
    return {"strategies": REGISTRY.reload()}


@router.get("/data-snapshots")
def snapshots():
    return [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "data" / "manifests").glob("*.yml"))
    ]


@router.post("/backtests", status_code=202)
def create_backtest(request: BacktestCreate):
    return {"run_id": submit_backtest(request.model_dump()), "status": "queued"}


@router.get("/backtests")
def list_backtests():
    rows = DB.query("SELECT * FROM runs ORDER BY created_at DESC LIMIT 50")
    for row in rows:
        row["request"] = json.loads(row.pop("request_json"))
    return rows


@router.get("/backtests/{run_id}")
def backtest(run_id: str):
    rows = DB.query("SELECT * FROM runs WHERE id=?", (run_id,))
    if not rows:
        raise HTTPException(404, "Run not found")
    row = rows[0]
    row["request"] = json.loads(row.pop("request_json"))
    return row


@router.get("/backtests/{run_id}/results")
def backtest_results(run_id: str):
    status = backtest(run_id)
    if status["status"] != "completed":
        raise HTTPException(409, f"Run is {status['status']}")
    return get_result(run_id)


@router.post("/comparisons")
def compare(request: ComparisonCreate):
    results = []
    for run_id in request.run_ids:
        try:
            result = get_result(run_id)
            results.append(
                {"run_id": run_id, "metrics": result["metrics"], "equity": result["equity"]}
            )
        except FileNotFoundError as exc:
            raise HTTPException(404, f"Result not found: {run_id}") from exc
    return {"runs": results}


@router.get("/experiments")
def experiments():
    rows = DB.query("SELECT * FROM experiments ORDER BY created_at DESC")
    return [{**json.loads(row["payload_json"]), "created_at": row["created_at"]} for row in rows]


@router.post("/experiments", status_code=201)
def create_experiment(request: ExperimentCreate):
    try:
        DB.add_experiment(
            request.experiment_id, request.model_dump(), datetime.now(timezone.utc).isoformat()
        )
    except Exception as exc:
        raise HTTPException(409, "Experiment ID already exists") from exc
    return request
