from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class MarketFrame:
    data: pd.DataFrame
    snapshot_id: str
    sha256: str

    def prices(self) -> pd.DataFrame:
        return self.data.pivot(index="date", columns="symbol", values="close").sort_index()


class DataProvider(ABC):
    @abstractmethod
    def load(
        self,
        symbols: Iterable[str],
        start: str,
        end: str,
        fields: Iterable[str],
        as_of: str | None = None,
    ) -> MarketFrame:
        raise NotImplementedError


class SnapshotProvider(DataProvider):
    def __init__(self, project_root: Path, snapshot_id: str):
        self.root = project_root
        self.snapshot_id = snapshot_id
        manifest_path = self.root / "data" / "manifests" / f"{snapshot_id}.yml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Unknown snapshot: {snapshot_id}")
        import yaml

        self.manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    def load(self, symbols, start, end, fields, as_of=None) -> MarketFrame:
        requested = {"date", "symbol", *fields}
        allowed = set(self.manifest["fields"])
        if not requested <= allowed:
            raise ValueError(f"Fields unavailable: {sorted(requested - allowed)}")
        path = self.root / self.manifest["path"]
        frame = pd.read_csv(path, parse_dates=["date"], dtype={"symbol": "string"})
        selected = frame[
            frame["symbol"].isin(list(symbols))
            & frame["date"].between(pd.Timestamp(start), pd.Timestamp(end))
        ].copy()
        if as_of:
            selected = selected[selected["date"] <= pd.Timestamp(as_of)]
        if selected.empty:
            raise ValueError("No market rows match the request")
        return MarketFrame(
            selected[list(requested)].sort_values(["date", "symbol"]),
            self.snapshot_id,
            self.manifest["sha256"],
        )
