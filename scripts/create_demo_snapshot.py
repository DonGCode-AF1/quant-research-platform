"""Create a deterministic synthetic ETF-like snapshot for pipeline tests."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ID = "demo-cn-etf-synthetic-v1"


def main() -> None:
    rng = np.random.default_rng(20260622)
    dates = pd.bdate_range("2020-01-02", "2025-12-31")
    symbols = ["510300", "510500", "512100", "512480", "512690", "515000"]
    market = rng.normal(0.0002, 0.008, len(dates))
    rows = []
    for index, symbol in enumerate(symbols):
        idiosyncratic = rng.normal(0.00002 * index, 0.005 + index * 0.0004, len(dates))
        close = 100 * np.exp(np.cumsum(market * (0.7 + index * 0.04) + idiosyncratic))
        amount = np.exp(rng.normal(19 + index * 0.15, 0.35, len(dates)))
        rows.extend(
            {
                "date": date.date().isoformat(),
                "symbol": symbol,
                "close": round(price, 6),
                "amount": round(value, 2),
            }
            for date, price, value in zip(dates, close, amount, strict=True)
        )
    frame = pd.DataFrame(rows).sort_values(["date", "symbol"])
    snapshot_dir = ROOT / "data" / "snapshots" / SNAPSHOT_ID
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    csv_path = snapshot_dir / "market.csv"
    frame.to_csv(csv_path, index=False)
    digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    manifest = {
        "id": SNAPSHOT_ID,
        "name": "合成中国ETF软件验收快照",
        "source": "deterministic synthetic generator",
        "license": "MIT (generated fixture)",
        "synthetic": True,
        "path": f"data/snapshots/{SNAPSHOT_ID}/market.csv",
        "coverage": {"start": "2020-01-02", "end": "2025-12-31"},
        "symbols": symbols,
        "fields": ["date", "symbol", "close", "amount"],
        "sha256": digest,
        "generated_by": "scripts/create_demo_snapshot.py",
    }
    manifest_dir = ROOT / "data" / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / f"{SNAPSHOT_ID}.yml").write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    print(f"created {SNAPSHOT_ID}: {len(frame)} rows, sha256={digest}")


if __name__ == "__main__":
    main()
