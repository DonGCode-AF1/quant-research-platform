from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
TABLE_DIR = ROOT / "assets" / "tables"
FIG_DIR = ROOT / "assets" / "figures" / "chapter5"
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
            "axes.unicode_minus": False,
        },
    )


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


def fig_component_interpretation() -> None:
    comp = read_csv(TABLE_DIR / "component_ablation.csv")
    comp = numeric(comp, ["cagr", "sharpe", "max_drawdown", "annual_gross_turnover"])
    comp = comp[comp["period"] == "full_walk_forward"].copy()
    labels = {
        "ranking_only": "仅因子排序",
        "ranking_plus_trend": "排序 + 趋势过滤",
        "ranking_plus_inverse_vol": "排序 + 反波动率",
        "complete_base": "完整基准策略",
    }
    order = ["ranking_only", "ranking_plus_trend", "ranking_plus_inverse_vol", "complete_base"]
    plot = comp.set_index("component").loc[order].reset_index()
    plot["label"] = plot["component"].map(labels)

    fig = plt.figure(figsize=(13.0, 7.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.0], left=0.08, right=0.97, top=0.78, bottom=0.16, wspace=0.28)
    ax_s = fig.add_subplot(gs[0, 0])
    ax_d = fig.add_subplot(gs[0, 1])
    add_header(
        fig,
        "策略组件对风险调整收益和回撤的影响",
        "组件拆解使用同一基准框架；比较仅排序、排序加趋势过滤、排序加反波动率和完整基准策略。",
    )
    colors = [NEUTRAL["base"], BLUE["mid"], ORANGE["base"], GOLD["mid"]]
    y = np.arange(len(plot))
    ax_s.barh(y, plot["sharpe"], color=colors, edgecolor=NEUTRAL["dark"], linewidth=0.6)
    ax_s.set_yticks(y, plot["label"])
    ax_s.invert_yaxis()
    ax_s.set_xlabel("Sharpe")
    ax_s.set_title("风险调整收益", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    for i, v in enumerate(plot["sharpe"]):
        ax_s.text(v + 0.025, i, f"{v:.2f}", va="center", ha="left", fontsize=9.5, color=TOKENS["ink"], fontweight="semibold")
    style_axis(ax_s, grid_axis="x")

    ax_d.barh(y, plot["max_drawdown"], color=colors, edgecolor=NEUTRAL["dark"], linewidth=0.6)
    ax_d.set_yticks(y, plot["label"])
    ax_d.invert_yaxis()
    ax_d.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax_d.set_xlabel("最大回撤")
    ax_d.set_title("下行风险", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    ax_d.axvline(0, color=NEUTRAL["dark"], linewidth=0.9)
    for i, v in enumerate(plot["max_drawdown"]):
        ax_d.text(v + 0.018, i, pct_text(v), va="center", ha="left", fontsize=9.5, color=TOKENS["ink"], fontweight="semibold")
    style_axis(ax_d, grid_axis="x")
    save(fig, "fig5_1_component_interpretation")


def fig_ml_role_map() -> None:
    fig, ax = plt.subplots(figsize=(13.0, 7.0))
    fig.subplots_adjust(left=0.055, right=0.97, top=0.78, bottom=0.10)
    add_header(
        fig,
        "机器学习在策略系统中的功能位置",
        "本研究的机器学习更接近研究治理工具：处理弱信号、降低共线性影响、辅助规格比较，而非给出因果解释。",
    )
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    boxes = [
        (0.04, 0.55, 0.20, 0.23, "可交易数据", "价格、成交额、波动、趋势\n行业ETF共同样本"),
        (0.30, 0.55, 0.22, 0.23, "机器学习层", "Ridge / LASSO / Elastic Net\n排序、收缩、变量筛选"),
        (0.58, 0.55, 0.18, 0.23, "交易规则层", "Top-K、趋势过滤\n月中调仓、T+1、成本"),
        (0.82, 0.55, 0.14, 0.23, "组合输出", "低频行业轮动\n有限风险暴露"),
        (0.30, 0.16, 0.22, 0.19, "审查层", "规格搜索、PBO\n滚动起点、市场状态"),
        (0.58, 0.16, 0.18, 0.19, "解释层", "收益来源拆解\n趋势与行业Beta择时"),
    ]
    for x, y, w, h, title, body in boxes:
        fc = BLUE["xlight"] if "机器学习" in title else (GOLD["xlight"] if title in ["交易规则层", "解释层"] else TOKENS["panel"])
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            linewidth=1.0,
            edgecolor=NEUTRAL["base"],
            facecolor=fc,
        )
        ax.add_patch(patch)
        ax.text(x + 0.018, y + h - 0.055, title, ha="left", va="center", fontsize=13, fontweight="semibold", color=TOKENS["ink"])
        ax.text(x + 0.018, y + h - 0.125, body, ha="left", va="top", fontsize=10.2, color=TOKENS["muted"], linespacing=1.45)

    def arrow(a: tuple[float, float], b: tuple[float, float], rad: float = 0.0) -> None:
        ax.add_patch(
            FancyArrowPatch(
                a,
                b,
                arrowstyle="-|>",
                mutation_scale=13,
                connectionstyle=f"arc3,rad={rad}",
                linewidth=1.2,
                color=NEUTRAL["mid"],
            )
        )

    arrow((0.24, 0.665), (0.30, 0.665))
    arrow((0.52, 0.665), (0.58, 0.665))
    arrow((0.76, 0.665), (0.82, 0.665))
    arrow((0.68, 0.55), (0.68, 0.35))
    arrow((0.58, 0.25), (0.52, 0.25))
    arrow((0.41, 0.35), (0.41, 0.55), rad=-0.18)
    ax.text(
        0.055,
        0.31,
        "关键边界：\n模型不直接决定仓位比例；\n模型也不能把相关性解释为因果关系。",
        ha="left",
        va="top",
        fontsize=11,
        color=TOKENS["ink"],
        bbox=dict(boxstyle="round,pad=0.45,rounding_size=0.025", facecolor=NEUTRAL["xlight"], edgecolor=NEUTRAL["light"]),
    )
    save(fig, "fig5_2_ml_role_map")


def fig_simple_ensemble_comparison() -> None:
    alg = read_csv(MVP_OUT / "algorithm_comparison_tests" / "algorithm_summary.csv")
    alg = numeric(alg, ["mean_sharpe", "min_sharpe", "mean_turnover"])
    alg_labels = {
        "历史正IC加权": "历史IC正向加权",
        "历史IC有符号加权": "历史IC有符号加权",
        "等权Z分数": "等权Z分数",
        "Rank投票": "Rank投票",
        "监督定向PCA1": "监督PCA",
        "Ridge": "Ridge",
        "Winsorized Ridge": "Winsorized Ridge",
        "Elastic Net": "Elastic Net",
        "Lasso": "LASSO",
    }
    alg["label"] = alg["algorithm_label"].map(alg_labels).fillna(alg["algorithm_label"])
    alg = alg.sort_values("mean_sharpe", ascending=True)

    conv = read_csv(MVP_OUT / "final_converged_compare" / "comparison_metrics.csv")
    conv = numeric(conv, ["cagr", "sharpe", "max_drawdown"])
    conv = conv[conv["period"] == "全共同样本"].copy()
    conv_labels = {
        "最新收束版_Ridge5": "五因子 Ridge",
        "昨日探索版_Enhanced8": "八因子固定合成",
        "8因子_Ridge": "八因子 Ridge",
        "沪深300ETF": "沪深300ETF",
        "6ETF等权": "行业ETF静态配置",
    }
    conv["label"] = conv["strategy"].map(conv_labels).fillna(conv["strategy"])
    conv_order = ["沪深300ETF", "行业ETF静态配置", "五因子 Ridge", "八因子 Ridge", "八因子固定合成"]
    conv["label"] = pd.Categorical(conv["label"], conv_order, ordered=True)
    conv = conv.sort_values("label")

    fig = plt.figure(figsize=(13.2, 7.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.05], left=0.12, right=0.97, top=0.78, bottom=0.13, wspace=0.32)
    ax_alg = fig.add_subplot(gs[0, 0])
    ax_conv = fig.add_subplot(gs[0, 1])
    add_header(
        fig,
        "固定因子合成与正则化排序模型的绩效比较",
        "左侧比较多种排序算法的平均 Sharpe；右侧比较收束阶段的五因子 Ridge、八因子 Ridge 和八因子固定合成。",
    )
    y = np.arange(len(alg))
    colors = [BLUE["mid"] if "等权" in label or "IC" in label or "Rank" in label else NEUTRAL["base"] for label in alg["label"]]
    ax_alg.barh(y, alg["mean_sharpe"], color=colors, edgecolor=NEUTRAL["dark"], linewidth=0.55)
    ax_alg.set_yticks(y, alg["label"])
    ax_alg.set_xlabel("平均 Sharpe")
    ax_alg.set_title("排序算法横向比较", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    for i, v in enumerate(alg["mean_sharpe"]):
        ax_alg.text(v + 0.025, i, f"{v:.2f}", va="center", ha="left", fontsize=9, color=TOKENS["ink"])
    style_axis(ax_alg, grid_axis="x")

    x = np.arange(len(conv))
    ax_conv.scatter(conv["sharpe"], conv["cagr"], s=170, color=[GOLD["mid"] if "固定合成" in str(v) else BLUE["mid"] if "Ridge" in str(v) else NEUTRAL["base"] for v in conv["label"]], edgecolor=NEUTRAL["dark"], linewidth=0.8)
    offsets = {
        "五因子 Ridge": (0.018, -0.006),
        "八因子 Ridge": (0.018, 0.006),
        "八因子固定合成": (0.018, 0.002),
        "沪深300ETF": (0.018, -0.002),
        "行业ETF静态配置": (0.018, 0.002),
    }
    for _, row in conv.iterrows():
        dx, dy = offsets.get(str(row["label"]), (0.015, 0.002))
        ax_conv.text(row["sharpe"] + dx, row["cagr"] + dy, str(row["label"]), fontsize=9.3, color=TOKENS["ink"], ha="left", va="center")
    ax_conv.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax_conv.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax_conv.set_xlabel("Sharpe")
    ax_conv.set_ylabel("年化收益")
    ax_conv.set_title("收束阶段关键版本", loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
    style_axis(ax_conv, grid_axis="both")
    save(fig, "fig5_3_simple_ensemble_comparison")


def fig_three_empirical_lessons() -> None:
    specs = read_csv(TABLE_DIR / "deep_final_robustness_unique.csv")
    specs = numeric(specs, ["S"])
    universe = specs.groupby("U", as_index=False)["S"].mean()
    universe["label"] = universe["U"].map({"6ETF": "宽口径行业池", "8ETF": "扩展行业池", "12ETF": "细分行业池"})
    universe["label"] = pd.Categorical(universe["label"], ["宽口径行业池", "扩展行业池", "细分行业池"], ordered=True)
    universe = universe.sort_values("label")

    factor = read_csv(MVP_OUT / "adaptive_wall_factor_report" / "adaptive_wall_scheme_summary.csv")
    factor = numeric(factor, ["mean_sharpe", "n_factors"])
    factor = factor[factor["scheme_id"].isin(["base5_equal", "notion_equal", "expanded_equal", "compact_ridge"])].copy()
    factor["label"] = factor["scheme_id"].map(
        {
            "base5_equal": "基准因子固定合成",
            "notion_equal": "核心因子固定合成",
            "expanded_equal": "全量因子固定合成",
            "compact_ridge": "紧凑因子 Ridge",
        }
    )
    factor["label"] = pd.Categorical(
        factor["label"],
        ["基准因子固定合成", "核心因子固定合成", "全量因子固定合成", "紧凑因子 Ridge"],
        ordered=True,
    )
    factor = factor.sort_values("label")

    freq = read_csv(TABLE_DIR / "frequency_robustness.csv")
    freq = numeric(freq, ["sharpe", "annual_gross_turnover"])
    freq = freq[(freq["period"] == "full_walk_forward") & (freq["cost_bps"] == 15)].copy()
    freq["label"] = freq["rebalance_mode"].map({"monthly": "月度调仓", "10d": "10日调仓", "weekly": "周度调仓", "daily": "日度调仓", "event_triggered": "事件触发"})
    freq["label"] = pd.Categorical(freq["label"], ["月度调仓", "10日调仓", "周度调仓", "日度调仓", "事件触发"], ordered=True)
    freq = freq.sort_values("label")

    fig = plt.figure(figsize=(13.4, 7.2))
    gs = fig.add_gridspec(1, 3, left=0.07, right=0.98, top=0.78, bottom=0.18, wspace=0.34)
    add_header(
        fig,
        "资产池、因子复杂度与交易频率的边际效应比较",
        "三个面板分别对应资产池颗粒度、因子复杂度和调仓频率；指标统一使用 Sharpe 或平均 Sharpe。",
    )
    panels = [
        (universe["label"].astype(str), universe["S"], "资产池颗粒度", "平均 Sharpe", BLUE["mid"]),
        (factor["label"].astype(str), factor["mean_sharpe"], "因子复杂度", "平均 Sharpe", GOLD["mid"]),
        (freq["label"].astype(str), freq["sharpe"], "交易频率", "Sharpe", ORANGE["base"]),
    ]
    for i, (labels, values, title, ylabel, color) in enumerate(panels):
        ax = fig.add_subplot(gs[0, i])
        x = np.arange(len(values))
        ax.bar(x, values, color=color, edgecolor=NEUTRAL["dark"], linewidth=0.6, alpha=0.92)
        ax.set_xticks(x, labels, rotation=28, ha="right")
        ax.set_title(title, loc="left", fontsize=12, fontweight="semibold", color=TOKENS["ink"], pad=10)
        ax.set_ylabel(ylabel if i == 0 else "")
        for j, v in enumerate(values):
            ax.text(j, v + 0.025, f"{v:.2f}", ha="center", va="bottom", fontsize=9.2, color=TOKENS["ink"], fontweight="semibold")
        style_axis(ax, grid_axis="y")
    save(fig, "fig5_4_three_empirical_lessons")


def main() -> None:
    setup_theme()
    fig_component_interpretation()
    fig_ml_role_map()
    fig_simple_ensemble_comparison()
    fig_three_empirical_lessons()
    print(f"Generated Chapter 5 figures in {FIG_DIR}")


if __name__ == "__main__":
    main()
