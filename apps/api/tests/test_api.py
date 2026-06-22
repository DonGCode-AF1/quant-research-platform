import time

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_strategy_and_snapshot_endpoints():
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/strategies").json()[0]["id"] == "equal_weight"
    assert client.get("/api/data-snapshots").json()[0]["synthetic"] is True


def test_backtest_lifecycle():
    response = client.post(
        "/api/backtests",
        json={
            "strategy_id": "equal_weight",
            "snapshot_id": "demo-cn-etf-synthetic-v1",
            "symbols": ["510300", "510500"],
            "start": "2021-01-01",
            "end": "2021-12-31",
            "parameters": {"cash_buffer": 0.05},
        },
    )
    assert response.status_code == 202
    run_id = response.json()["run_id"]
    status = "queued"
    for _ in range(50):
        status = client.get(f"/api/backtests/{run_id}").json()["status"]
        if status in {"completed", "failed"}:
            break
        time.sleep(0.1)
    assert status == "completed"
    result = client.get(f"/api/backtests/{run_id}/results").json()
    assert "sharpe" in result["metrics"]
    assert result["provenance"]["data_hash"]
