from __future__ import annotations

import json
from pathlib import Path


def write_result(result, run_dir: Path, provenance: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    result.equity.to_csv(run_dir / "equity.csv", index=False)
    result.trades.to_csv(run_dir / "trades.csv", index=False)
    result.weights.to_csv(run_dir / "weights.csv", index=False)
    payload = {
        "metrics": result.metrics,
        "request": result.request,
        "warnings": result.warnings,
        "provenance": provenance,
    }
    (run_dir / "result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
