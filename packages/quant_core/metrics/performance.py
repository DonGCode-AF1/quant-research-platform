import math

import pandas as pd


def calculate_metrics(returns: pd.Series, turnover: pd.Series) -> dict[str, float]:
    returns = returns.fillna(0.0)
    years = max(len(returns) / 252, 1 / 252)
    total = float((1 + returns).prod() - 1)
    cagr = float((1 + total) ** (1 / years) - 1) if total > -1 else -1.0
    vol = float(returns.std(ddof=0) * math.sqrt(252))
    sharpe = (
        float(returns.mean() / returns.std(ddof=0) * math.sqrt(252)) if returns.std(ddof=0) else 0.0
    )
    equity = (1 + returns).cumprod()
    max_drawdown = float((equity / equity.cummax() - 1).min())
    return {
        "total_return": total,
        "cagr": cagr,
        "volatility": vol,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "annual_turnover": float(turnover.sum() / years),
    }
