from typing import Any

from pydantic import BaseModel, Field


class BacktestCreate(BaseModel):
    strategy_id: str
    strategy_version: str = "1.0.0"
    parameters: dict[str, Any] = Field(default_factory=dict)
    snapshot_id: str
    symbols: list[str]
    start: str
    end: str
    initial_capital: float = 1_000_000
    rebalance: str = "month_end"
    commission_bps: float = 5
    slippage_bps: float = 5
    t_plus_one: bool = True
    seed: int = 42


class ComparisonCreate(BaseModel):
    run_ids: list[str] = Field(min_length=2)


class ExperimentCreate(BaseModel):
    experiment_id: str
    question: str
    hypothesis: str
    primary_change: str
    metrics: list[str]
    run_ids: list[str] = Field(default_factory=list)
