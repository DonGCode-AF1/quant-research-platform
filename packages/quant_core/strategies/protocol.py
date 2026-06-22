from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, TypeAlias

import pandas as pd

TargetWeights: TypeAlias = dict[str, float]


@dataclass(frozen=True)
class StrategyContext:
    signal_date: pd.Timestamp
    prices: pd.DataFrame
    current_weights: TargetWeights


class StrategyPlugin(Protocol):
    def generate_targets(
        self, context: StrategyContext, parameters: dict[str, Any]
    ) -> TargetWeights: ...
