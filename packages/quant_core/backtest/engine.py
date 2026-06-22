from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from ..metrics import calculate_metrics
from ..strategies import StrategyContext, StrategyRegistry


@dataclass(frozen=True)
class BacktestRequest:
    strategy_id: str
    strategy_version: str
    parameters: dict[str, Any]
    snapshot_id: str
    symbols: list[str]
    start: str
    end: str
    initial_capital: float = 1_000_000
    rebalance: str = "month_end"
    commission_bps: float = 5.0
    slippage_bps: float = 5.0
    t_plus_one: bool = True
    seed: int = 42


@dataclass
class BacktestResult:
    metrics: dict[str, float]
    equity: pd.DataFrame
    trades: pd.DataFrame
    weights: pd.DataFrame
    request: dict[str, Any]
    warnings: list[str]


class BacktestEngine:
    """Long-only close-to-close engine with signal at t and execution at t+1 close."""

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def run(self, request: BacktestRequest, market) -> BacktestResult:
        item = self.registry.get(request.strategy_id)
        prices = market.prices().reindex(columns=request.symbols).ffill()
        if prices.isna().all().any():
            raise ValueError("At least one symbol has no prices in the selected interval")
        dates = prices.index
        signal_dates = self._signal_dates(prices, request.rebalance)
        pending: dict[pd.Timestamp, dict[str, float]] = {}
        for signal_date in signal_dates:
            pos = dates.get_loc(signal_date)
            if pos + 1 >= len(dates):
                continue
            context = StrategyContext(signal_date, prices.loc[:signal_date], {})
            targets = item.module.generate_targets(context, request.parameters)
            self._validate_targets(targets, request.symbols)
            pending[dates[pos + 1]] = targets

        current = {symbol: 0.0 for symbol in request.symbols}
        daily_returns = prices.pct_change().fillna(0.0)
        rows, trades, weights = [], [], []
        equity = 1.0
        cost_rate = (request.commission_bps + request.slippage_bps) / 10_000
        for i, date in enumerate(dates):
            turnover = 0.0
            if date in pending:
                target = pending[date]
                turnover = sum(abs(target.get(s, 0.0) - current[s]) for s in current)
                for symbol in current:
                    delta = target.get(symbol, 0.0) - current[symbol]
                    if abs(delta) > 1e-12:
                        trades.append(
                            {
                                "date": date,
                                "symbol": symbol,
                                "weight_change": delta,
                                "price": prices.at[date, symbol],
                            }
                        )
                    current[symbol] = target.get(symbol, 0.0)
            gross = 0.0 if i == 0 else sum(current[s] * daily_returns.at[date, s] for s in current)
            net = gross - turnover * cost_rate
            equity *= 1 + net
            rows.append(
                {
                    "date": date,
                    "return": net,
                    "equity": equity,
                    "drawdown": 0.0,
                    "turnover": turnover,
                }
            )
            weights.extend({"date": date, "symbol": s, "weight": w} for s, w in current.items())
        curve = pd.DataFrame(rows).set_index("date")
        curve["drawdown"] = curve["equity"] / curve["equity"].cummax() - 1
        metrics = calculate_metrics(curve["return"], curve["turnover"])
        return BacktestResult(
            metrics,
            curve.reset_index(),
            pd.DataFrame(trades),
            pd.DataFrame(weights),
            asdict(request),
            [],
        )

    @staticmethod
    def _signal_dates(prices: pd.DataFrame, frequency: str) -> list[pd.Timestamp]:
        if frequency == "daily":
            return list(prices.index)
        if frequency == "weekly":
            return list(prices.groupby(prices.index.to_period("W")).tail(1).index)
        if frequency == "month_end":
            return list(prices.groupby(prices.index.to_period("M")).tail(1).index)
        raise ValueError(f"Unsupported rebalance frequency: {frequency}")

    @staticmethod
    def _validate_targets(targets: dict[str, float], universe: list[str]) -> None:
        unknown = set(targets) - set(universe)
        if unknown:
            raise ValueError(f"Target contains unknown symbols: {sorted(unknown)}")
        if any(weight < 0 for weight in targets.values()):
            raise ValueError("This engine version only supports long-only targets")
        if sum(targets.values()) > 1.000001:
            raise ValueError("Target weights exceed 100%")
