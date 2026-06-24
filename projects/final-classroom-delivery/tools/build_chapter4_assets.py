from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
TABLE_DIR = ROOT / "assets" / "tables"
FIG_DIR = ROOT / "assets" / "figures" / "chapter4"
MVP_OUT = WORKSPACE / "mvp_cn" / "outputs"

FIG_DIR.mkdir(parents=True, exist_ok=True)

TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
}
NEUTRAL = {"xlight": "#F4F5F7", "light": "#E2E5EA", "base": "#C5CAD3", "mid": "#7A828F", "dark": "#464C55"}
BLUE = {"xlight": "#EAF1FE", "light": "#CEDFFE", "base": "#A3BEFA", "mid": "#5477C4", "dark": "#2E4780"}
GOLD = {"xlight": "#FFF4C2", "light": "#FFEA8F", "base": "#FFE15B", "mid": "#B8A037", "dark": "#736422"}
ORANGE = {"xlight": "#FFEDDE", "light": "#FFBDA1", "base": "#F0986E", "mid": "#CC6F47", "dark": "#804126"}
OLIVE = {"xlight": "#D8ECBD", "light": "#BEEB96", "base": "#A3D576", "mid": "#71B436", "dark": "#386411"}


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", **kwargs)


def setup_theme() -> None:
    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.facecolor": TOKENS["surface"],
            "savefig.facecolor": TOKENS["surface"],
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "axes.labelcolor": TOKENS["ink"],
            "grid.color": TOKENS["grid"],
            "grid.linewidth": 0.75,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.family": "sans-serif",
            "font.sans-serif": ["Microsoft YaHei", "Noto Sans CJK SC", "SimHei", "Segoe UI", "DejaVu Sans"],
            "font.monospace": ["Consolas", "DejaVu Sans Mono", "monospace"],
            "axes.unicode_minus": False,
        },
    )
    plt.rcParams["axes.unicode_minus"] = False


def numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def add_header(fig: plt.Figure, title: str, subtitle: str, *, left: float = 0.055, y: float = 0.965) -> None:
    fig.text(left, y, title, ha="left", va="top", fontsize=17, fontweight="semibold", color=TOKENS["ink"])
    fig.text(left, y - 0.045, subtitle, ha="left", va="top", fontsize=10.5, color=TOKENS["muted"])


def style_axis(ax: plt.Axes, *, grid_axis: str = "y") -> None:
    ax.set_facecolor(TOKENS["panel"])
    for side in ("left", "bottom"):
        ax.spines[side].set_color(TOKENS["axis"])
        ax.spines[side].set_linewidth(1.0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=TOKENS["muted"], labelsize=9)
    ax.grid(False)
    if grid_axis:
        ax.grid(True, axis=grid_axis, color=TOKENS["grid"], linewidth=0.75)


def save(fig: plt.Figure, name: str) -> None:
    for ext in ("png", "svg"):
        fig.savefig(FIG_DIR / f"{name}.{ext}", dpi=220, bbox_inches="tight", facecolor=TOKENS["surface"])
    plt.close(fig)


def pct_text(v: float, digits: int = 1) -> str:
    return f"{v * 100:.{digits}f}%"


def nav_from_returns(df: pd.DataFrame, col: str) -> pd.DataFrame:
    sub = df[["date", col]].copy()
    sub[col] = pd.to_numeric(sub[col], errors="coerce").fillna(0)
    sub["nav"] = (1 + sub[col]).cumprod()
    return sub[["date", "nav"]]


def drawdown(nav: pd.Series) -> pd.Series:
    return nav / nav.cummax() - 1


def perf_from_returns(r: pd.Series, periods: int = 252) -> dict[str, float]:
    r = pd.to_numeric(r, errors="coerce").dropna()
    if len(r) == 0:
        return {"cagr": np.nan, "vol": np.nan, "sharpe": np.nan, "max_drawdown": np.nan, "total_return": np.nan}
    nav = (1 + r).cumprod()
    years = max(len(r) / periods, 1 / periods)
    cagr = nav.iloc[-1] ** (1 / years) - 1
    vol = r.std(ddof=0) * np.sqrt(periods)
    sharpe = (r.mean() / r.std(ddof=0) * np.sqrt(periods)) if r.std(ddof=0) > 0 else np.nan
    return {"cagr": cagr, "vol": vol, "sharpe": sharpe, "max_drawdown": drawdown(nav).min(), "total_return": nav.iloc[-1] - 1}


def final_return_frame() -> pd.DataFrame:
    df = read_csv(MVP_OUT / "ma180_final" / "ma180_final_returns.csv", parse_dates=["date"])
    return df.rename(
        columns={
            "月中15日_增强因子_策略": "优化后策略",
            "月中15日_增强因子_沪深300": "沪深300ETF",
            "月中15日_增强因子_等权": "行业ETF静态配置",
        }
    )


def fig_final_vs_benchmark_panel() -> None:
    returns = final_return_frame()
    metrics = read_csv(MVP_OUT / "ma180_final" / "ma180_final_metrics.csv")
    metrics = numeric(metrics, ["cagr", "sharpe", "max_drawdown", "monthly_win_rate", "annual_gross_turnover"])
    final = metrics[(metrics["配置"] == "月中15日_增强因子") & (metrics["时期"] == "全样本")].iloc[0]

    series_map = {
        "优化后策略": (BLUE["mid"], "-"),
        "沪深300ETF": (NEUTRAL["dark"], (0, (2, 2))),
        "行业ETF静态配置": (GOLD["mid"], "-"),
    }

    fig = plt.figure(figsize=(13.2, 7.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 0.95], left=0.07, right=0.97, top=0.78, bottom=0.12, wspace=0.28)
    ax_nav = fig.add_subplot(gs[0, 0])
    ax_dd = fig.add_subplot(gs[0, 1])
    add_header(
        fig,
        "优化后策略与主要基准的净值和回撤比较",
        "最终口径采用六类宽口径行业ETF、扩展量价因子、月中调仓、180日均线趋势过滤、T+1执行与交易成本约束。",
    )

    for col, (color, linestyle) in series_map.items():
        nav = nav_from_returns(returns, col)
        ax_nav.plot(nav["date"], nav["nav"], color=color, linestyle=linestyle, linewidth=1.55, label=col)
        ax_dd.plot(nav["date"], drawdown(nav["nav"]), color=color, linestyle=linestyle, linewidth=1.15, label=col)
    ax_nav.set_title("累计净值", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_nav.set_ylabel("累计净值")
    ax_nav.set_xlabel("")
    locator = mdates.AutoDateLocator(minticks=4, maxticks=6)
    ax_nav.xaxis.set_major_locator(locator)
    ax_nav.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    style_axis(ax_nav, grid_axis="y")
    ax_nav.legend(frameon=False, loc="upper left", fontsize=8.8, ncol=2)

    ax_dd.set_title("回撤路径", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_dd.set_ylabel("相对历史峰值回撤")
    ax_dd.set_xlabel("")
    ax_dd.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax_dd.xaxis.set_major_locator(locator)
    ax_dd.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    style_axis(ax_dd, grid_axis="y")
    ax_dd.text(
        0.02,
        -0.16,
        f"优化后策略：CAGR {pct_text(final['cagr'])}，Sharpe {final['sharpe']:.2f}，最大回撤 {pct_text(final['max_drawdown'])}。",
        transform=ax_dd.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color=TOKENS["muted"],
    )
    save(fig, "fig4_1_final_vs_benchmark_panel")


def fig_key_versions_scorecard() -> None:
    rows = [
        ("月末基准因子", "月末_原因子", "全样本"),
        ("月中调仓", "月中15日_原因子", "全样本"),
        ("优化后策略", "月中15日_增强因子", "全样本"),
        ("优化后策略 开发期", "月中15日_增强因子", "开发期"),
        ("优化后策略 冻结期", "月中15日_增强因子", "冻结期"),
    ]
    metrics = read_csv(MVP_OUT / "ma180_final" / "ma180_final_metrics.csv")
    metrics = numeric(metrics, ["cagr", "sharpe", "max_drawdown", "monthly_win_rate", "annual_gross_turnover"])
    selected = []
    for label, cfg, period in rows:
        mask = (metrics["配置"].astype(str).str.strip() == cfg) & (metrics["时期"].astype(str).str.strip() == period)
        if not mask.any():
            raise ValueError(f"Missing metric row: {cfg} / {period}")
        r = metrics.loc[mask].iloc[0].to_dict()
        r["展示版本"] = label
        selected.append(r)
    df = pd.DataFrame(selected)
    idx = df["展示版本"].tolist()
    values = pd.DataFrame(
        {
            "年化收益": df["cagr"].to_numpy(),
            "Sharpe": df["sharpe"].to_numpy(),
            "最大回撤": df["max_drawdown"].to_numpy(),
            "月度胜率": df["monthly_win_rate"].to_numpy(),
            "年化换手率": df["annual_gross_turnover"].to_numpy(),
        },
        index=idx,
    )
    score = pd.DataFrame(index=idx)
    labels = pd.DataFrame(index=idx)
    for col in values.columns:
        s = values[col].astype(float)
        rank_source = -s if col == "年化换手" else s
        score[col] = rank_source.rank(pct=True)
        if col in ["年化收益", "最大回撤", "月度胜率"]:
            labels[col] = s.map(lambda x: pct_text(x))
        elif col == "年化换手率":
            labels[col] = s.map(lambda x: f"{x:.1f}x")
        else:
            labels[col] = s.map(lambda x: f"{x:.2f}")

    cmap = LinearSegmentedColormap.from_list("score", [NEUTRAL["xlight"], BLUE["xlight"], BLUE["base"], GOLD["light"]])
    fig, ax = plt.subplots(figsize=(12.6, 6.7))
    fig.subplots_adjust(left=0.20, right=0.98, top=0.78, bottom=0.12)
    add_header(
        fig,
        "主要策略规格的绩效比较",
        "同一数据口径下比较调仓日、因子组与开发/冻结区间表现；颜色越深表示同列相对更优，换手按较低值优先处理。",
    )
    ax.imshow(score.values, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(values.columns)), values.columns)
    ax.set_yticks(np.arange(len(idx)), idx)
    ax.tick_params(length=0, labelsize=10)
    for i in range(score.shape[0]):
        for j in range(score.shape[1]):
            ax.text(j, i, labels.iloc[i, j], ha="center", va="center", fontsize=10, fontweight="semibold", color=TOKENS["ink"])
    for x in np.arange(-0.5, len(values.columns), 1):
        ax.axvline(x, color=TOKENS["panel"], linewidth=2)
    for y in np.arange(-0.5, len(idx), 1):
        ax.axhline(y, color=TOKENS["panel"], linewidth=2)
    sns.despine(ax=ax, left=True, bottom=True)
    save(fig, "fig4_2_key_versions_scorecard")


def fig_spec_search_risk_panel() -> None:
    specs = read_csv(TABLE_DIR / "deep_final_robustness_unique.csv")
    specs = numeric(specs, ["S", "C", "D", "calmar"])
    asset_labels = {"6ETF": "六类宽口径", "8ETF": "八类扩展", "12ETF": "十二类细分"}
    specs["资产池"] = specs["U"].map(asset_labels).fillna(specs["U"])
    summary = specs.groupby(["资产池", "model_norm"], as_index=False).agg(
        mean_sharpe=("S", "mean"),
        p75=("S", lambda x: x.quantile(0.75)),
        n=("S", "size"),
    )
    order = summary.groupby("资产池")["mean_sharpe"].mean().sort_values(ascending=False).index.tolist()
    summary["资产池"] = pd.Categorical(summary["资产池"], order, ordered=True)
    summary = summary.sort_values(["资产池", "model_norm"])

    fig = plt.figure(figsize=(13.0, 7.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1.05], left=0.08, right=0.97, top=0.78, bottom=0.12, wspace=0.28)
    ax_hist = fig.add_subplot(gs[0, 0])
    ax_heat = fig.add_subplot(gs[0, 1])
    add_header(
        fig,
        "规格搜索分布与过拟合风险诊断",
        "左侧展示近百组策略规格的 Sharpe 分布，右侧按资产池与模型汇总平均 Sharpe；重点是识别稳定区域而非单一最优值。",
    )
    ax_hist.hist(specs["S"].dropna(), bins=22, color=BLUE["base"], edgecolor=BLUE["dark"], linewidth=1.0)
    ax_hist.axvline(specs["S"].median(), color=NEUTRAL["dark"], linestyle=":", linewidth=1.2, label=f"中位数 {specs['S'].median():.2f}")
    ax_hist.axvline(specs["S"].quantile(0.90), color=GOLD["dark"], linestyle=":", linewidth=1.2, label=f"90分位 {specs['S'].quantile(0.90):.2f}")
    ax_hist.set_title("规格 Sharpe 分布", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_hist.set_xlabel("Sharpe")
    ax_hist.set_ylabel("规格数量")
    ax_hist.legend(frameon=False, fontsize=8.8)
    style_axis(ax_hist, grid_axis="y")

    matrix = summary.pivot(index="资产池", columns="model_norm", values="mean_sharpe").sort_index()
    cmap = LinearSegmentedColormap.from_list("heat", [NEUTRAL["xlight"], BLUE["xlight"], BLUE["base"], GOLD["light"]])
    sns.heatmap(matrix, ax=ax_heat, cmap=cmap, linewidths=1, linecolor=TOKENS["panel"], annot=True, fmt=".2f", cbar=False)
    ax_heat.set_title("资产池 x 模型 平均 Sharpe", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_heat.set_xlabel("")
    ax_heat.set_ylabel("")
    ax_heat.tick_params(axis="x", rotation=0)
    ax_heat.tick_params(axis="y", rotation=0)
    save(fig, "fig4_3_spec_search_risk_panel")


def fig_wall_sensitivity_panel() -> None:
    returns = final_return_frame().sort_values("date")
    cols = ["优化后策略", "沪深300ETF", "行业ETF静态配置"]
    first, last = returns["date"].min(), returns["date"].max()
    walls = pd.date_range(first + pd.DateOffset(years=3), last - pd.DateOffset(months=6), freq="6MS")
    rows = []
    for wall in walls:
        sub = returns[returns["date"] >= wall]
        for col in cols:
            metric = perf_from_returns(sub[col])
            rows.append({"评价起点": wall, "序列": col, **metric})
    wall_df = pd.DataFrame(rows)
    pivot = wall_df.pivot(index="评价起点", columns="序列", values="sharpe")[cols]

    fig, ax = plt.subplots(figsize=(12.4, 6.9))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.78, bottom=0.15)
    add_header(
        fig,
        "滚动评价起点下的 Sharpe 稳定性",
        "每半年移动一次评价起点，并重新计算优化后策略、沪深300ETF和行业ETF静态配置的 Sharpe；这是滚动起点敏感性检查，不等同于真正未来检验。",
    )
    colors = {"优化后策略": BLUE["mid"], "沪深300ETF": NEUTRAL["dark"], "行业ETF静态配置": GOLD["mid"]}
    styles = {"优化后策略": "-", "沪深300ETF": (0, (2, 2)), "行业ETF静态配置": "-"}
    for col in cols:
        ax.plot(pivot.index, pivot[col], marker="o", linewidth=1.45, color=colors[col], linestyle=styles[col], label=col)
    ax.axhline(0, color=NEUTRAL["light"], linewidth=1.0)
    ax.set_ylabel("Sharpe")
    ax.set_xlabel("评价起点")
    locator = mdates.AutoDateLocator(minticks=5, maxticks=8)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    style_axis(ax, grid_axis="y")
    save(fig, "fig4_4_wall_sensitivity_panel")


def fig_market_regime_panel() -> None:
    returns = final_return_frame().sort_values("date")
    cols = ["优化后策略", "沪深300ETF", "行业ETF静态配置"]
    for col in cols:
        returns[col] = pd.to_numeric(returns[col], errors="coerce").fillna(0)
    bench_nav = (1 + returns["沪深300ETF"]).cumprod()
    bench_dd = drawdown(bench_nav)
    returns["市场状态"] = np.select(
        [bench_dd <= -0.20, bench_dd <= -0.05],
        ["大盘深回撤", "大盘普通回撤"],
        default="大盘高位或上行",
    )
    order = ["大盘深回撤", "大盘普通回撤", "大盘高位或上行"]
    rows = []
    for state in order:
        sub = returns[returns["市场状态"] == state]
        for col in cols:
            metric = perf_from_returns(sub[col])
            rows.append({"市场状态": state, "序列": col, **metric})
    regime = pd.DataFrame(rows)
    excess = (
        returns.groupby("市场状态")
        .apply(
            lambda g: pd.Series(
                {
                    "优化后策略": (g["优化后策略"] - g["沪深300ETF"]).mean() * 252,
                    "行业ETF静态配置": (g["行业ETF静态配置"] - g["沪深300ETF"]).mean() * 252,
                }
            ),
            include_groups=False,
        )
        .reindex(order)
    )

    fig = plt.figure(figsize=(13.0, 7.3))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], left=0.08, right=0.97, top=0.78, bottom=0.12, wspace=0.24)
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_excess = fig.add_subplot(gs[0, 1])
    add_header(
        fig,
        "市场状态分组下的条件收益比较",
        "按沪深300ETF自身回撤状态进行描述性切分；该图用于解释收益来源，不用于宣称策略能够预知市场状态。",
    )
    palette = {"优化后策略": BLUE["mid"], "沪深300ETF": NEUTRAL["dark"], "行业ETF静态配置": GOLD["mid"]}
    x = np.arange(len(order))
    width = 0.24
    for i, series in enumerate(cols):
        part = regime[regime["序列"] == series].set_index("市场状态").loc[order]
        ax_bar.bar(x + (i - 1) * width, part["cagr"], width=width, color=palette[series], edgecolor=NEUTRAL["dark"], linewidth=0.6, label=series)
    ax_bar.axhline(0, color=NEUTRAL["dark"], linewidth=1.0)
    ax_bar.set_xticks(x, order)
    ax_bar.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax_bar.set_ylabel("条件年化收益")
    ax_bar.set_title("按大盘回撤状态切分的收益", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_bar.legend(frameon=False, fontsize=8.8, ncol=3)
    style_axis(ax_bar, grid_axis="y")

    for i, series in enumerate(["优化后策略", "行业ETF静态配置"]):
        ax_excess.bar(x + (i - 0.5) * 0.28, excess[series], width=0.28, color=palette[series], edgecolor=NEUTRAL["dark"], linewidth=0.6, label=series)
    ax_excess.axhline(0, color=NEUTRAL["dark"], linewidth=1.0)
    ax_excess.set_xticks(x, order)
    ax_excess.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax_excess.set_ylabel("相对沪深300ETF的年化平均收益差")
    ax_excess.set_title("相对大盘的条件超额", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_excess.legend(frameon=False, fontsize=8.8)
    style_axis(ax_excess, grid_axis="y")
    save(fig, "fig4_5_market_regime_panel")


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    setup_theme()
    fig_final_vs_benchmark_panel()
    fig_key_versions_scorecard()
    fig_spec_search_risk_panel()
    fig_wall_sensitivity_panel()
    fig_market_regime_panel()
    print(f"Generated Chapter 4 figures in {FIG_DIR}")


if __name__ == "__main__":
    main()
