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
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
TABLE_DIR = ROOT / "assets" / "tables"
FIG_DIR = ROOT / "assets" / "figures" / "chapter3"
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

NEUTRAL = {
    "xlight": "#F4F5F7",
    "light": "#E2E5EA",
    "base": "#C5CAD3",
    "mid": "#7A828F",
    "dark": "#464C55",
}

BLUE = {"xlight": "#EAF1FE", "light": "#CEDFFE", "base": "#A3BEFA", "mid": "#5477C4", "dark": "#2E4780"}
GOLD = {"xlight": "#FFF4C2", "light": "#FFEA8F", "base": "#FFE15B", "mid": "#B8A037", "dark": "#736422"}
ORANGE = {"xlight": "#FFEDDE", "light": "#FFBDA1", "base": "#F0986E", "mid": "#CC6F47", "dark": "#804126"}
OLIVE = {"xlight": "#D8ECBD", "light": "#BEEB96", "base": "#A3D576", "mid": "#71B436", "dark": "#386411"}
PINK = {"xlight": "#FCDAD6", "light": "#F5BACC", "base": "#F390CA", "mid": "#BD569B", "dark": "#8A3A6F"}


FACTOR_LABELS = {
    "mom_21": "短期动量",
    "mom_63": "中期动量",
    "mom_126": "长期动量",
    "trend_quality_63": "趋势质量",
    "low_vol_63": "低波动",
    "low_downside_vol_63": "下行波动防御",
    "distance_ma_20": "短均线距离",
    "distance_ma_200": "长期均线距离",
    "reversal_21": "短期反转",
    "drawdown_resilience_63": "回撤修复",
    "low_beta_126": "低市场敏感度",
    "skew_63": "收益偏度",
    "amount_surprise_120": "成交额异常",
    "nonzero_return_share_63": "价格更新活跃度",
    "gap_return_20": "跳空收益",
    "intraday_return_20": "日内收益",
    "range_compression_20": "振幅收缩",
    "price_volume_corr_63": "价量相关",
    "volume_acceleration_20_120": "成交加速",
    "turnover_stability_63": "换手稳定性",
    "close_position_20": "收盘位置",
    "close_location_20": "收盘位置",
    "mom_252": "252日动量",
    "trend_quality_126": "126日趋势质量",
    "reversal_5": "5日反转",
    "skip_recent_mom_252_21": "跳过近月的长动量",
    "trend_efficiency_63": "趋势效率",
}

STRATEGY_LABELS = {
    "6ETF_5因子Ridge": "六类宽口径 · 五因子 Ridge",
    "8ETF_5因子Ridge": "八类扩展 · 五因子 Ridge",
    "6ETF_8因子Ridge": "六类宽口径 · 扩展因子 Ridge",
    "8ETF_8因子Ridge": "八类扩展 · 扩展因子 Ridge",
    "6ETF_8因子等权": "六类宽口径 · 扩展因子固定合成",
    "8ETF_8因子等权": "八类扩展 · 扩展因子固定合成",
}

PERIOD_LABELS = {
    "full_walk_forward": "全样本",
    "development": "开发期",
    "seen_holdout": "冻结期",
    "全样本": "全样本",
    "开发期": "开发期",
    "冻结期": "冻结期",
}

FREQ_LABELS = {
    "monthly": "月频",
    "10d": "10日",
    "weekly": "周频",
    "daily": "日频",
    "event_triggered": "事件触发",
}

MODEL_LABELS = {
    "benchmark": "沪深300ETF",
    "legacy_monthly_ridge5": "五因子 Ridge（月频）",
    "stability_lasso_ridge": "LASSO筛选 + Ridge",
    "elastic_net": "Elastic Net",
}


def setup_theme() -> None:
    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.facecolor": TOKENS["surface"],
            "savefig.facecolor": TOKENS["surface"],
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "axes.labelcolor": TOKENS["ink"],
            "axes.grid": True,
            "grid.color": TOKENS["grid"],
            "grid.linewidth": 0.75,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Microsoft YaHei",
                "Noto Sans CJK SC",
                "Source Han Sans SC",
                "SimHei",
                "Segoe UI",
                "DejaVu Sans",
            ],
            "font.monospace": ["Consolas", "DejaVu Sans Mono", "monospace"],
            "axes.unicode_minus": False,
        },
    )
    plt.rcParams["axes.unicode_minus"] = False


def save(fig: plt.Figure, name: str) -> None:
    for ext in ("png", "svg"):
        fig.savefig(FIG_DIR / f"{name}.{ext}", dpi=220, bbox_inches="tight", facecolor=TOKENS["surface"])
    plt.close(fig)


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


def pct(value: float, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def fig_asset_pool_scorecard() -> None:
    df = pd.read_csv(TABLE_DIR / "strategy_metrics_extended.csv")
    df = numeric(
        df,
        [
            "cagr",
            "sharpe",
            "max_drawdown",
            "calmar",
            "monthly_win_rate",
            "annual_gross_turnover",
            "avg_position_count",
        ],
    )
    strategies = list(STRATEGY_LABELS)
    plot_df = df[df["strategy"].isin(strategies)].drop_duplicates("strategy").set_index("strategy").loc[strategies]

    metrics = [
        ("cagr", "年化收益", True, lambda v: pct(v)),
        ("sharpe", "Sharpe", True, lambda v: f"{v:.2f}"),
        ("max_drawdown", "最大回撤", True, lambda v: pct(v)),
        ("monthly_win_rate", "月度胜率", True, lambda v: pct(v)),
        ("annual_gross_turnover", "年化换手", False, lambda v: f"{v:.1f}x"),
    ]

    score = pd.DataFrame(index=strategies)
    labels = pd.DataFrame(index=strategies)
    for col, label, higher_better, fmt in metrics:
        s = plot_df[col].astype(float)
        rank_source = s if higher_better else -s
        score[label] = rank_source.rank(pct=True)
        labels[label] = s.map(fmt)

    cmap = LinearSegmentedColormap.from_list("scorecard", [NEUTRAL["xlight"], BLUE["xlight"], BLUE["base"], GOLD["light"]])
    fig, ax = plt.subplots(figsize=(12.4, 6.9))
    fig.subplots_adjust(left=0.275, right=0.98, top=0.78, bottom=0.11)
    add_header(
        fig,
        "资产池比较：扩容需要带来独立信息，而不只是增加排序维度",
        "共同样本内比较六类宽口径与八类扩展资产池；颜色越深表示该指标在同列中越优，年化换手按越低越优处理。",
    )
    ax.imshow(score.values, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(metrics)), [m[1] for m in metrics], fontsize=10, color=TOKENS["ink"])
    ax.set_yticks(np.arange(len(strategies)), [STRATEGY_LABELS[s] for s in strategies], fontsize=10, color=TOKENS["ink"])
    ax.tick_params(length=0)

    for i in range(score.shape[0]):
        for j in range(score.shape[1]):
            ax.text(j, i, labels.iloc[i, j], ha="center", va="center", fontsize=10, color=TOKENS["ink"], fontweight="semibold")

    for x in np.arange(-0.5, len(metrics), 1):
        ax.axvline(x, color=TOKENS["panel"], linewidth=2)
    for y in np.arange(-0.5, len(strategies), 1):
        ax.axhline(y, color=TOKENS["panel"], linewidth=2)

    ax.set_xlim(-0.5, len(metrics) - 0.5)
    ax.set_ylim(len(strategies) - 0.5, -0.5)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.text(
        -0.06,
        -0.13,
        "说明：固定合成指因子得分按预设方向合成后排序，仍采用 Top-K 与趋势过滤，不涉及仓位比例优化。",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color=TOKENS["muted"],
    )
    sns.despine(ax=ax, left=True, bottom=True)
    save(fig, "fig3_1_asset_pool_scorecard")


def fig_factor_governance_funnel() -> None:
    df = pd.read_csv(TABLE_DIR / "factor_candidate_screen.csv")
    status_counts = df["status"].value_counts()
    new_candidates = len(df[df["status"] != "existing"])
    retained = int(status_counts.get("candidate", 0) + status_counts.get("strong_candidate", 0))
    lasso = pd.read_csv(TABLE_DIR / "lasso_selection_frequency.csv")
    stable_lasso = (
        lasso.groupby("factor")["selection_frequency"].mean().reset_index().query("selection_frequency >= 0.60").shape[0]
    )

    fig, ax = plt.subplots(figsize=(12.4, 5.8))
    fig.subplots_adjust(left=0.04, right=0.98, top=0.86, bottom=0.09)
    add_header(
        fig,
        "因子治理流程：从候选变量扩张转向信号筛选与审查",
        "候选因子先通过覆盖率、冗余度与分期 IC 过滤，再进入 LASSO 稳定性筛选和回测审查。",
    )
    ax.set_axis_off()
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 4.1)

    stages = [
        (0.35, 2.82, 1.95, 1.05, "初始量价因子", "5 个", "动量、趋势、波动"),
        (2.75, 2.82, 2.05, 1.05, "扩展候选维度", f"{new_candidates} 个", "成交、跳空、回撤等"),
        (5.25, 2.82, 2.05, 1.05, "第一轮治理", "三层过滤", "覆盖率、冗余度、分期 IC"),
        (7.75, 2.82, 2.05, 1.05, "保留候选", f"{retained} 个", "候选或强候选"),
        (10.05, 2.82, 1.95, 1.05, "稳定性审查", f"{stable_lasso} 个", "LASSO 高频入选"),
    ]
    colors = [BLUE, GOLD, ORANGE, OLIVE, PINK]

    for idx, (x, y, w, h, title, count, desc) in enumerate(stages):
        family = colors[idx]
        box = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.022,rounding_size=0.10",
            facecolor=family["xlight"],
            edgecolor=family["dark"],
            linewidth=1.35,
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h * 0.73, title, ha="center", va="center", fontsize=11, fontweight="semibold", color=TOKENS["ink"])
        ax.text(x + w / 2, y + h * 0.47, count, ha="center", va="center", fontsize=12, fontweight="semibold", color=family["dark"])
        ax.text(x + w / 2, y + h * 0.22, desc, ha="center", va="center", fontsize=9.3, color=TOKENS["ink"])
        if idx < len(stages) - 1:
            x2 = stages[idx + 1][0]
            ax.add_patch(
                FancyArrowPatch(
                    (x + w + 0.10, y + h / 2),
                    (x2 - 0.12, y + h / 2),
                    arrowstyle="-|>",
                    mutation_scale=14,
                    linewidth=1.2,
                    color=NEUTRAL["dark"],
                )
            )

    exclusions = [
        ("覆盖不足", int(status_counts.get("insufficient_coverage", 0)), 4.95, 1.55, ORANGE),
        ("高度冗余", int(status_counts.get("redundant", 0)), 6.35, 1.55, ORANGE),
        ("弱或不稳定", int(status_counts.get("weak_or_unstable", 0)), 7.75, 1.55, ORANGE),
    ]
    ax.text(6.65, 1.00, "未直接进入最终规格的主要原因", ha="center", va="center", fontsize=10, color=TOKENS["muted"])
    for label, count, x, y, family in exclusions:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                1.15,
                0.72,
                boxstyle="round,pad=0.02,rounding_size=0.08",
                facecolor=family["xlight"],
                edgecolor=family["mid"],
                linewidth=1.0,
            )
        )
        ax.text(x + 0.575, y + 0.46, label, ha="center", va="center", fontsize=9.5, color=TOKENS["ink"])
        ax.text(x + 0.575, y + 0.18, f"{count} 个", ha="center", va="center", fontsize=10, fontweight="semibold", color=family["dark"])
    ax.add_patch(
        FancyArrowPatch(
            (6.30, 2.82),
            (6.30, 2.34),
            connectionstyle="arc3,rad=0.0",
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.0,
            color=NEUTRAL["mid"],
        )
    )
    ax.text(
        0.35,
        0.38,
        "读图方式：这不是一次性“挑最优因子”，而是把变量扩张后的研究者自由度前置为可审查步骤。",
        fontsize=9.5,
        color=TOKENS["muted"],
    )
    save(fig, "fig3_2_factor_governance_funnel")


def fig_factor_stability_lasso_panel() -> None:
    screen = pd.read_csv(TABLE_DIR / "factor_candidate_screen.csv")
    screen = numeric(
        screen,
        ["ic_2018_2020", "ic_2021_2022", "ic_2023_2024", "ic_2025_2026", "mean_spearman_ic", "max_abs_corr_with_existing"],
    )
    status_order = {"existing": 0, "strong_candidate": 1, "candidate": 2, "redundant": 3}
    selected = screen[screen["status"].isin(status_order)].copy()
    selected["status_rank"] = selected["status"].map(status_order)
    selected = selected.sort_values(["status_rank", "mean_spearman_ic"], ascending=[True, False]).head(18)
    selected["因子"] = selected["factor"].map(lambda x: FACTOR_LABELS.get(x, x))
    heat_cols = ["ic_2018_2020", "ic_2021_2022", "ic_2023_2024", "ic_2025_2026"]
    heat = selected.set_index("因子")[heat_cols]
    heat.columns = ["2018-2020", "2021-2022", "2023-2024", "2025-2026"]

    lasso = pd.read_csv(TABLE_DIR / "lasso_selection_frequency.csv")
    lasso = numeric(lasso, ["selection_frequency", "mean_abs_lasso_coefficient"])
    freq = (
        lasso.groupby("factor", as_index=False)
        .agg(selection_frequency=("selection_frequency", "mean"), mean_abs_lasso_coefficient=("mean_abs_lasso_coefficient", "mean"))
        .sort_values("selection_frequency", ascending=False)
        .head(11)
    )
    freq["因子"] = freq["factor"].map(lambda x: FACTOR_LABELS.get(x, x))

    fig = plt.figure(figsize=(13.4, 8.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 0.95], left=0.08, right=0.97, top=0.79, bottom=0.10, wspace=0.30)
    ax_heat = fig.add_subplot(gs[0, 0])
    ax_bar = fig.add_subplot(gs[0, 1])
    add_header(
        fig,
        "因子证据面板：分期 IC 检查方向，LASSO 检查入选稳定性",
        "左侧为分期 Spearman IC，右侧为不同训练期中 LASSO 的平均入选频率；二者共同用于判断候选信号是否值得进入策略比较。",
    )

    cmap = LinearSegmentedColormap.from_list("ic_diverge", [ORANGE["base"], TOKENS["panel"], BLUE["base"]])
    sns.heatmap(
        heat,
        ax=ax_heat,
        cmap=cmap,
        norm=TwoSlopeNorm(vmin=-0.16, vcenter=0, vmax=0.22),
        linewidths=1.0,
        linecolor=TOKENS["panel"],
        annot=True,
        fmt=".2f",
        cbar_kws={"label": "IC"},
        annot_kws={"fontsize": 8, "color": TOKENS["ink"]},
    )
    ax_heat.set_title("分期横截面 IC", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_heat.set_xlabel("")
    ax_heat.set_ylabel("")
    ax_heat.tick_params(axis="x", rotation=0)
    ax_heat.tick_params(axis="y", rotation=0)

    plot = freq.sort_values("selection_frequency", ascending=True)
    colors = [GOLD["base"] if v >= 0.75 else BLUE["base"] if v >= 0.60 else NEUTRAL["base"] for v in plot["selection_frequency"]]
    edges = [GOLD["dark"] if v >= 0.75 else BLUE["dark"] if v >= 0.60 else NEUTRAL["dark"] for v in plot["selection_frequency"]]
    bars = ax_bar.barh(plot["因子"], plot["selection_frequency"], color=colors, edgecolor=edges, linewidth=1.0)
    for bar, value in zip(bars, plot["selection_frequency"]):
        ax_bar.text(value + 0.018, bar.get_y() + bar.get_height() / 2, f"{value:.2f}", ha="left", va="center", fontsize=9, color=TOKENS["ink"])
    ax_bar.axvline(0.60, color=NEUTRAL["dark"], linewidth=1.0, linestyle=":")
    ax_bar.text(
        0.60,
        1.015,
        "60%参考线",
        transform=ax_bar.get_xaxis_transform(),
        ha="center",
        va="bottom",
        fontsize=8.5,
        color=NEUTRAL["dark"],
    )
    ax_bar.set_xlim(0, 1.08)
    ax_bar.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax_bar.set_title("LASSO 入选频率", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_bar.set_xlabel("平均入选频率")
    ax_bar.set_ylabel("")
    style_axis(ax_bar, grid_axis="x")
    save(fig, "fig3_3_factor_stability_lasso_panel")


def _cum_nav_from_returns(df: pd.DataFrame, col: str) -> pd.Series:
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    return (1 + s).cumprod()


def fig_model_window_panel() -> None:
    returns = pd.read_csv(MVP_OUT / "model_comparison" / "main_daily_returns.csv", parse_dates=["date"])
    metrics = pd.read_csv(TABLE_DIR / "training_window_robustness.csv")
    metrics = numeric(metrics, ["sharpe", "cagr", "max_drawdown", "annual_gross_turnover"])

    fig = plt.figure(figsize=(13.0, 7.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 0.95], left=0.07, right=0.97, top=0.78, bottom=0.11, wspace=0.28)
    ax_line = fig.add_subplot(gs[0, 0])
    ax_dot = fig.add_subplot(gs[0, 1])
    add_header(
        fig,
        "模型与训练窗口：正则化主要承担收缩和稳定排序功能",
        "左侧比较正则化模型的累计净值路径，右侧比较 5 年滚动、8 年滚动和扩展窗口在全样本/开发期/冻结期的 Sharpe。",
    )

    colors = {
        "benchmark": NEUTRAL["mid"],
        "legacy_monthly_ridge5": BLUE["mid"],
        "stability_lasso_ridge": GOLD["mid"],
        "elastic_net": ORANGE["mid"],
    }
    styles = {
        "benchmark": (0, (2, 2)),
        "legacy_monthly_ridge5": "-",
        "stability_lasso_ridge": "-",
        "elastic_net": "-.",
    }
    for col in ["benchmark", "legacy_monthly_ridge5", "stability_lasso_ridge", "elastic_net"]:
        valid = returns[["date", col]].dropna()
        nav = (1 + pd.to_numeric(valid[col], errors="coerce")).cumprod()
        ax_line.plot(valid["date"], nav, color=colors[col], linewidth=1.55, linestyle=styles[col], label=MODEL_LABELS[col])
    ax_line.set_title("正则化模型累计净值", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_line.set_ylabel("累计净值")
    ax_line.set_xlabel("")
    ax_line.set_yscale("log")
    ax_line.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
    locator = mdates.AutoDateLocator(minticks=4, maxticks=6)
    ax_line.xaxis.set_major_locator(locator)
    ax_line.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    style_axis(ax_line, grid_axis="y")
    ax_line.legend(frameon=False, loc="upper left", fontsize=8.6, ncol=2, handlelength=2.4)

    period_order = ["development", "full_walk_forward", "seen_holdout"]
    window_order = ["rolling_5y", "rolling_8y", "expanding"]
    window_labels = {"rolling_5y": "5年滚动", "rolling_8y": "8年滚动", "expanding": "扩展窗口"}
    period_colors = {"development": BLUE["base"], "full_walk_forward": GOLD["base"], "seen_holdout": OLIVE["base"]}
    offsets = {"development": -0.16, "full_walk_forward": 0.0, "seen_holdout": 0.16}
    y_positions = {w: i for i, w in enumerate(window_order)}
    for period in period_order:
        part = metrics[(metrics["period"] == period) & (metrics["train_mode"].isin(window_order))]
        for _, row in part.iterrows():
            y = y_positions[row["train_mode"]] + offsets[period]
            ax_dot.scatter(
                row["sharpe"],
                y,
                s=120,
                facecolor=period_colors[period],
                edgecolor=NEUTRAL["dark"],
                linewidth=0.8,
                label=PERIOD_LABELS[period],
                zorder=3,
            )
            ax_dot.text(row["sharpe"] + 0.018, y, f"{row['sharpe']:.2f}", ha="left", va="center", fontsize=8.5, color=TOKENS["ink"])
    handles, labels = ax_dot.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax_dot.legend(by_label.values(), by_label.keys(), frameon=False, loc="upper left", fontsize=8.6)
    ax_dot.set_yticks(list(y_positions.values()), [window_labels[w] for w in window_order])
    ax_dot.set_xlabel("Sharpe")
    ax_dot.set_ylabel("")
    ax_dot.set_title("训练窗口稳健性", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_dot.set_xlim(0.15, 1.26)
    style_axis(ax_dot, grid_axis="x")
    save(fig, "fig3_4_model_window_panel")


def fig_frequency_cost_panel() -> None:
    returns = pd.read_csv(MVP_OUT / "second_round" / "frequency_daily_returns.csv", parse_dates=["date"])
    metrics = pd.read_csv(TABLE_DIR / "frequency_robustness.csv")
    metrics = numeric(metrics, ["cost_bps", "sharpe", "cagr", "max_drawdown", "annual_gross_turnover"])
    metrics = metrics[(metrics["period"] == "full_walk_forward") & (metrics["cost_bps"] == 15)].copy()
    order = ["monthly", "weekly", "10d", "daily", "event_triggered"]
    metrics["rebalance_mode"] = pd.Categorical(metrics["rebalance_mode"], order, ordered=True)
    metrics = metrics.sort_values("rebalance_mode")

    fig = plt.figure(figsize=(13.0, 7.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 0.95], left=0.07, right=0.97, top=0.78, bottom=0.11, wspace=0.27)
    ax_line = fig.add_subplot(gs[0, 0])
    ax_scatter = fig.add_subplot(gs[0, 1])
    add_header(
        fig,
        "交易频率：更快响应会同时放大换手、成本和噪声",
        "单边 15bp 成本口径；左侧为不同调仓频率的累计净值，右侧为 Sharpe 与年化换手的关系。",
    )

    palette = {
        "monthly": BLUE["mid"],
        "weekly": GOLD["mid"],
        "10d": ORANGE["mid"],
        "daily": PINK["mid"],
        "event_triggered": NEUTRAL["dark"],
    }
    for mode in order:
        col = f"{mode}__15bp"
        if col not in returns:
            continue
        valid = returns[["date", col]].dropna()
        nav = (1 + pd.to_numeric(valid[col], errors="coerce")).cumprod()
        ax_line.plot(valid["date"], nav, color=palette[mode], linewidth=1.55, label=FREQ_LABELS[mode], linestyle="--" if mode == "event_triggered" else "-")
    ax_line.set_title("成本后累计净值", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_line.set_ylabel("累计净值")
    ax_line.set_xlabel("")
    locator = mdates.AutoDateLocator(minticks=4, maxticks=6)
    ax_line.xaxis.set_major_locator(locator)
    ax_line.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    style_axis(ax_line, grid_axis="y")
    ax_line.legend(frameon=False, loc="upper left", fontsize=8.6, ncol=3, handlelength=2.4)

    for _, row in metrics.iterrows():
        mode = str(row["rebalance_mode"])
        size = 90 + abs(row["max_drawdown"]) * 620
        ax_scatter.scatter(
            row["annual_gross_turnover"],
            row["sharpe"],
            s=size,
            facecolor=palette[mode],
            edgecolor=NEUTRAL["dark"],
            linewidth=0.9,
            alpha=0.86,
        )
        ax_scatter.text(
            row["annual_gross_turnover"] + 0.55,
            row["sharpe"] + (0.012 if mode != "weekly" else -0.025),
            FREQ_LABELS[mode],
            ha="left",
            va="center",
            fontsize=9,
            color=TOKENS["ink"],
        )
    monthly = metrics[metrics["rebalance_mode"] == "monthly"].iloc[0]
    ax_scatter.axhline(monthly["sharpe"], color=NEUTRAL["dark"], linestyle=":", linewidth=1.0)
    ax_scatter.axvline(monthly["annual_gross_turnover"], color=NEUTRAL["dark"], linestyle=":", linewidth=1.0)
    ax_scatter.set_title("换手与 Sharpe", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_scatter.set_xlabel("年化换手倍数")
    ax_scatter.set_ylabel("Sharpe")
    ax_scatter.set_xlim(0, max(metrics["annual_gross_turnover"]) + 7)
    ax_scatter.set_ylim(0.55, 1.02)
    style_axis(ax_scatter, grid_axis="both")
    ax_scatter.text(
        0.02,
        -0.16,
        "气泡大小表示最大回撤绝对值；越右表示交易越频繁。",
        transform=ax_scatter.transAxes,
        ha="left",
        va="top",
        fontsize=8.8,
        color=TOKENS["muted"],
    )
    save(fig, "fig3_5_frequency_cost_panel")


def fig_trend_filter_panel() -> None:
    ma200 = pd.read_csv(MVP_OUT / "ma_regime" / "ma_regime_metrics.csv")
    ma200 = numeric(ma200, ["sharpe", "max_drawdown", "cagr"])
    ma200 = ma200[ma200["过滤策略"] == "200MA(原始)"].copy()
    ma200["策略"] = "200MA 原始"

    ma180 = pd.read_csv(MVP_OUT / "ma180_final" / "ma180_final_metrics.csv")
    ma180 = numeric(ma180, ["sharpe", "max_drawdown", "cagr"])
    keep = ["月末_原因子", "月中15日_原因子", "月中15日_增强因子"]
    ma180 = ma180[ma180["配置"].isin(keep)].copy()
    ma180["策略"] = ma180["配置"].map(
        {
            "月末_原因子": "180MA 月末",
            "月中15日_原因子": "180MA 月中",
            "月中15日_增强因子": "180MA 月中增强",
        }
    )
    data = pd.concat(
        [
            ma200.rename(columns={"过滤策略": "配置"})[["策略", "时期", "sharpe", "max_drawdown", "cagr"]],
            ma180[["策略", "时期", "sharpe", "max_drawdown", "cagr"]],
        ],
        ignore_index=True,
    )
    period_order = ["开发期", "全样本", "冻结期"]
    strategy_order = ["200MA 原始", "180MA 月末", "180MA 月中", "180MA 月中增强"]
    data["时期"] = pd.Categorical(data["时期"], period_order, ordered=True)
    data["策略"] = pd.Categorical(data["策略"], strategy_order, ordered=True)
    data = data.sort_values(["策略", "时期"])

    fig = plt.figure(figsize=(13.2, 7.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], left=0.07, right=0.97, top=0.78, bottom=0.12, wspace=0.25)
    ax_line = fig.add_subplot(gs[0, 0])
    ax_bar = fig.add_subplot(gs[0, 1])
    add_header(
        fig,
        "趋势过滤：规则调整改善的是状态切换，而不是独立创造预测信息",
        "比较 200 日均线、180 日均线、月中调仓和增强因子规格；重点观察开发期、全样本与冻结期是否方向一致。",
    )
    palette = {
        "200MA 原始": NEUTRAL["dark"],
        "180MA 月末": ORANGE["mid"],
        "180MA 月中": BLUE["mid"],
        "180MA 月中增强": GOLD["mid"],
    }

    x = np.arange(len(period_order))
    for strategy in strategy_order:
        part = data[data["策略"] == strategy].set_index("时期").loc[period_order]
        ax_line.plot(x, part["sharpe"], marker="o", linewidth=1.55, color=palette[strategy], label=strategy.replace("\n", ""))
    ax_line.set_xticks(x, period_order)
    ax_line.set_ylabel("Sharpe")
    ax_line.set_xlabel("")
    ax_line.set_title("分期 Sharpe", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_line.set_xlim(-0.15, len(period_order) - 0.15)
    style_axis(ax_line, grid_axis="y")
    ax_line.legend(frameon=False, loc="upper left", fontsize=8.6, ncol=2)

    full = data[data["时期"] == "全样本"].copy()
    full["最大回撤(%)"] = full["max_drawdown"] * 100
    y = np.arange(len(strategy_order))
    bars = ax_bar.barh(
        y,
        full.set_index("策略").loc[strategy_order, "最大回撤(%)"],
        color=[palette[s] for s in strategy_order],
        edgecolor=NEUTRAL["dark"],
        linewidth=0.8,
    )
    for bar, value in zip(bars, full.set_index("策略").loc[strategy_order, "最大回撤(%)"]):
        ax_bar.text(value - 0.8, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", ha="right", va="center", fontsize=9, color=TOKENS["ink"])
    ax_bar.axvline(0, color=NEUTRAL["dark"], linewidth=1.0)
    ax_bar.set_yticks(y, strategy_order)
    ax_bar.set_title("全样本最大回撤", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_bar.set_xlabel("回撤")
    ax_bar.set_ylabel("")
    ax_bar.set_xlim(min(full["最大回撤(%)"]) - 4, 2)
    style_axis(ax_bar, grid_axis="x")
    save(fig, "fig3_6_trend_filter_panel")


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    setup_theme()
    fig_asset_pool_scorecard()
    fig_factor_governance_funnel()
    fig_factor_stability_lasso_panel()
    fig_model_window_panel()
    fig_frequency_cost_panel()
    fig_trend_filter_panel()
    print(f"Generated Chapter 3 figures in {FIG_DIR}")


if __name__ == "__main__":
    main()
