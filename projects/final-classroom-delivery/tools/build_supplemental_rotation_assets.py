from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
FIG_DIR = ROOT / "assets" / "figures" / "supplement"
TABLE_DIR = ROOT / "assets" / "tables" / "supplement"

WEIGHTS = WORKSPACE / "mvp_cn" / "outputs" / "ridge_target_weights.csv"
PRICES = WORKSPACE / "mvp_cn" / "data" / "processed" / "all_etf_prices.csv"

ETF_LABELS = {
    "sh510150": "消费",
    "sh510170": "商品资源",
    "sh510230": "金融",
    "sz159929": "医药",
    "sz159930": "能源",
    "sh512330": "信息技术",
}

ETF_FULL = {
    "sh510150": "招商消费ETF",
    "sh510170": "国联安大宗商品ETF",
    "sh510230": "国泰金融ETF",
    "sz159929": "汇添富医药ETF",
    "sz159930": "汇添富能源ETF",
    "sh512330": "南方信息科技ETF",
}

COLORS = {
    "sh510150": "#8c3f45",
    "sh510170": "#a98754",
    "sh510230": "#1f3f5c",
    "sz159929": "#607466",
    "sz159930": "#c26a3f",
    "sh512330": "#3f6c9f",
}


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.sans-serif": [
                "Microsoft YaHei",
                "SimHei",
                "Noto Sans CJK SC",
                "Arial Unicode MS",
            ],
            "axes.unicode_minus": False,
            "figure.dpi": 150,
            "savefig.dpi": 240,
            "axes.facecolor": "#fffdf8",
            "figure.facecolor": "#f7f3ea",
            "axes.edgecolor": "#d7ccba",
            "axes.labelcolor": "#263442",
            "xtick.color": "#4f5962",
            "ytick.color": "#4f5962",
            "text.color": "#263442",
        }
    )


def load_weights() -> pd.DataFrame:
    df = pd.read_csv(WEIGHTS)
    df["signal_date"] = pd.to_datetime(df["signal_date"])
    df = df.set_index("signal_date").sort_index()
    cols = [c for c in ETF_LABELS if c in df.columns]
    return df[cols].fillna(0.0)


def load_prices() -> pd.DataFrame:
    df = pd.read_csv(PRICES)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    cols = [c for c in ETF_LABELS if c in df.columns]
    return df[cols]


def year_ticks(index: pd.DatetimeIndex, step: int = 12) -> tuple[list[int], list[str]]:
    positions = list(range(0, len(index), step))
    labels = [index[i].strftime("%Y-%m") for i in positions]
    if positions[-1] != len(index) - 1:
        positions.append(len(index) - 1)
        labels.append(index[-1].strftime("%Y-%m"))
    return positions, labels


def plot_weight_heatmap(weights: pd.DataFrame) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    weights.to_csv(TABLE_DIR / "monthly_ridge_target_weights.csv", encoding="utf-8-sig")

    matrix = weights.T
    fig, ax = plt.subplots(figsize=(13.5, 5.7))
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "paper_red", ["#f7f3ea", "#d9b38c", "#8c3f45"]
    )
    vmax = min(1.0, max(0.45, float(matrix.values.max())))
    im = ax.imshow(matrix.values, aspect="auto", cmap=cmap, vmin=0, vmax=vmax)

    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels([ETF_LABELS[c] for c in matrix.index], fontsize=11)
    pos, lab = year_ticks(weights.index, 6)
    ax.set_xticks(pos)
    ax.set_xticklabels(lab, rotation=45, ha="right", fontsize=9)
    fig.suptitle("月度走步持仓权重：Ridge 排序策略", x=0.08, y=0.975, ha="left", fontsize=16, weight="bold", color="#162b3d")
    fig.text(
        0.08,
        0.925,
        "颜色越深表示目标权重越高；空白表示当月未入选或趋势过滤后未持有。",
        fontsize=10,
        color="#697482",
    )
    ax.set_xlabel("信号月份")
    ax.set_ylabel("行业 ETF")
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.015)
    cbar.ax.set_ylabel("目标权重", rotation=270, labelpad=16)
    fig.tight_layout(rect=[0, 0, 1, 0.89])
    fig.savefig(FIG_DIR / "fig_s1_monthly_ridge_weight_heatmap.png", bbox_inches="tight")
    plt.close(fig)


def plot_weight_area(weights: pd.DataFrame) -> None:
    selected = (weights > 0).sum(axis=1)
    selection_counts = pd.DataFrame(
        {
            "ETF代码": list(ETF_LABELS),
            "行业标签": [ETF_LABELS[c] for c in ETF_LABELS],
            "入选月份数": [(weights[c] > 0).sum() for c in ETF_LABELS],
            "平均持仓权重": [weights.loc[weights[c] > 0, c].mean() for c in ETF_LABELS],
        }
    )
    selection_counts.to_csv(TABLE_DIR / "ridge_selection_counts.csv", index=False, encoding="utf-8-sig")

    fig = plt.figure(figsize=(13.5, 7.5))
    gs = fig.add_gridspec(2, 1, height_ratios=[3.1, 1.25], hspace=0.22)
    ax = fig.add_subplot(gs[0])
    x = weights.index
    y = [weights[c].values for c in ETF_LABELS]
    ax.stackplot(x, y, labels=[ETF_LABELS[c] for c in ETF_LABELS], colors=[COLORS[c] for c in ETF_LABELS], alpha=0.9)
    ax.set_ylim(0, 1.02)
    fig.suptitle("月度走步持仓结构：机器学习排序后的规则化配置", x=0.08, y=0.975, ha="left", fontsize=16, weight="bold", color="#162b3d")
    fig.text(
        0.08,
        0.925,
        "Ridge 负责形成 ETF 相对排序；最终权重由 Top-K、趋势过滤与风险规则生成。",
        fontsize=10,
        color="#697482",
    )
    ax.set_ylabel("组合权重")
    ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.08), frameon=False, fontsize=9)
    ax.grid(axis="y", color="#ece4d6", linewidth=0.8)

    ax2 = fig.add_subplot(gs[1], sharex=ax)
    ax2.plot(x, selected.values, color="#162b3d", linewidth=1.8)
    ax2.fill_between(x, selected.values, color="#1f3f5c", alpha=0.18)
    ax2.set_ylim(-0.05, max(3.2, selected.max() + 0.25))
    ax2.set_ylabel("持有数量")
    ax2.set_xlabel("信号月份")
    ax2.grid(axis="y", color="#ece4d6", linewidth=0.8)
    fig.tight_layout(rect=[0, 0, 1, 0.89])
    fig.savefig(FIG_DIR / "fig_s2_monthly_ridge_weight_area.png", bbox_inches="tight")
    plt.close(fig)


def plot_price_trends(prices: pd.DataFrame) -> None:
    normed = prices.copy()
    for c in normed.columns:
        first = normed[c].first_valid_index()
        if first is not None:
            normed[c] = normed[c] / normed.loc[first, c]
    normed.to_csv(TABLE_DIR / "six_etf_price_index_since_inception.csv", encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    for c in ETF_LABELS:
        s = normed[c].dropna()
        ax.plot(s.index, s.values, label=ETF_LABELS[c], color=COLORS[c], linewidth=2.0)
    fig.suptitle("六类基础行业 ETF 自成立以来的价格趋势", x=0.08, y=0.975, ha="left", fontsize=16, weight="bold", color="#162b3d")
    fig.text(
        0.08,
        0.925,
        "每条曲线以该 ETF 首个可用交易日归一化为 1；图中比较的是长期价格路径而非策略收益。",
        fontsize=10,
        color="#697482",
    )
    ax.set_ylabel("归一化价格指数")
    ax.set_xlabel("日期")
    ax.grid(axis="y", color="#ece4d6", linewidth=0.8)
    ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.1), frameon=False, fontsize=9)
    fig.tight_layout(rect=[0, 0, 1, 0.89])
    fig.savefig(FIG_DIR / "fig_s3_six_etf_price_trends_since_inception.png", bbox_inches="tight")
    plt.close(fig)


def plot_rotation_map(prices: pd.DataFrame) -> None:
    monthly = prices.resample("ME").last()
    ret_6m = monthly.pct_change(6)
    ret_6m = ret_6m.dropna(how="all")
    ranks = ret_6m.rank(axis=1, ascending=False, method="min")
    ranks.to_csv(TABLE_DIR / "six_etf_rolling_6m_relative_strength_rank.csv", encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(13.5, 5.8))
    matrix = ranks[[c for c in ETF_LABELS]].T
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "rank_map", ["#8c3f45", "#d9b38c", "#f7f3ea", "#b7c0b3", "#1f3f5c"], N=6
    )
    im = ax.imshow(matrix.values, aspect="auto", cmap=cmap, vmin=1, vmax=6)
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels([ETF_LABELS[c] for c in matrix.index], fontsize=11)
    pos, lab = year_ticks(matrix.columns, 12)
    ax.set_xticks(pos)
    ax.set_xticklabels(lab, rotation=45, ha="right", fontsize=9)
    fig.suptitle("行业相对强弱轮动：滚动 6 个月收益排名", x=0.08, y=0.975, ha="left", fontsize=16, weight="bold", color="#162b3d")
    fig.text(
        0.08,
        0.925,
        "红色表示近 6 个月相对更强，蓝色表示相对更弱；横向颜色迁移可观察行业强弱切换。",
        fontsize=10,
        color="#697482",
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.015, ticks=[1, 2, 3, 4, 5, 6])
    cbar.ax.set_ylabel("相对强弱排名", rotation=270, labelpad=16)
    ax.set_xlabel("月份")
    ax.set_ylabel("行业 ETF")
    fig.tight_layout(rect=[0, 0, 1, 0.89])
    fig.savefig(FIG_DIR / "fig_s4_rolling_6m_rotation_rank_heatmap.png", bbox_inches="tight")
    plt.close(fig)

    winners = ranks.idxmin(axis=1).dropna()
    transitions = pd.crosstab(winners.shift(1), winners, normalize="index").fillna(0)
    transitions = transitions.reindex(index=list(ETF_LABELS), columns=list(ETF_LABELS)).fillna(0)
    transitions.to_csv(TABLE_DIR / "six_etf_relative_strength_transition_matrix.csv", encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7.8, 6.5))
    im = ax.imshow(transitions.values, cmap="YlOrBr", vmin=0, vmax=max(0.5, transitions.values.max()))
    ax.set_xticks(range(len(transitions.columns)))
    ax.set_xticklabels([ETF_LABELS[c] for c in transitions.columns], rotation=35, ha="right")
    ax.set_yticks(range(len(transitions.index)))
    ax.set_yticklabels([ETF_LABELS[c] for c in transitions.index])
    fig.suptitle("相对强势行业的月度转移矩阵", x=0.06, y=0.975, ha="left", fontsize=15, weight="bold", color="#162b3d")
    ax.set_xlabel("本月相对强势行业")
    ax.set_ylabel("上月相对强势行业")
    for i in range(transitions.shape[0]):
        for j in range(transitions.shape[1]):
            val = transitions.iat[i, j]
            ax.text(j, i, f"{val:.0%}", ha="center", va="center", fontsize=8, color="#162b3d" if val < 0.45 else "white")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(FIG_DIR / "fig_s5_relative_strength_transition_matrix.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    configure_style()
    weights = load_weights()
    prices = load_prices()
    plot_weight_heatmap(weights)
    plot_weight_area(weights)
    plot_price_trends(prices)
    plot_rotation_map(prices)
    print(f"Wrote figures to {FIG_DIR}")
    print(f"Wrote tables to {TABLE_DIR}")


if __name__ == "__main__":
    main()
