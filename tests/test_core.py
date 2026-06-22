from pathlib import Path

import pandas as pd
from quant_core.backtest import BacktestEngine, BacktestRequest
from quant_core.data import SnapshotProvider
from quant_core.strategies import StrategyRegistry

ROOT = Path(__file__).resolve().parents[1]


def test_registry_discovers_example():
    registry = StrategyRegistry(ROOT / "strategies")
    assert registry.reload()[0]["id"] == "equal_weight"


def test_snapshot_hash_and_backtest_are_reproducible():
    registry = StrategyRegistry(ROOT / "strategies")
    registry.reload()
    request = BacktestRequest(
        strategy_id="equal_weight",
        strategy_version="1.0.0",
        parameters={"cash_buffer": 0.1},
        snapshot_id="demo-cn-etf-synthetic-v1",
        symbols=["510300", "510500"],
        start="2021-01-01",
        end="2022-12-31",
    )
    market = SnapshotProvider(ROOT, request.snapshot_id).load(
        request.symbols, request.start, request.end, ["close"]
    )
    first = BacktestEngine(registry).run(request, market)
    second = BacktestEngine(registry).run(request, market)
    pd.testing.assert_frame_equal(first.equity, second.equity)
    assert first.trades.iloc[0]["date"] > pd.Timestamp("2021-01-01")
    assert first.metrics["annual_turnover"] > 0


def test_signal_executes_next_session_and_cost_reduces_equity():
    registry = StrategyRegistry(ROOT / "strategies")
    registry.reload()
    base = dict(
        strategy_id="equal_weight",
        strategy_version="1.0.0",
        parameters={},
        snapshot_id="demo-cn-etf-synthetic-v1",
        symbols=["510300", "510500"],
        start="2021-01-01",
        end="2021-06-30",
    )
    market = SnapshotProvider(ROOT, base["snapshot_id"]).load(
        base["symbols"], base["start"], base["end"], ["close"]
    )
    free = BacktestEngine(registry).run(
        BacktestRequest(**base, commission_bps=0, slippage_bps=0), market
    )
    costly = BacktestEngine(registry).run(
        BacktestRequest(**base, commission_bps=15, slippage_bps=15), market
    )
    assert costly.equity.iloc[-1]["equity"] < free.equity.iloc[-1]["equity"]
