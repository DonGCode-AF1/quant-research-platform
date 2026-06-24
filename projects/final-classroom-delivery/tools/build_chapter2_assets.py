from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[4]
MVP = ROOT / "mvp_cn"
DELIV = ROOT / "quant-research-platform" / "projects" / "final-classroom-delivery"
FIG = DELIV / "assets" / "figures" / "chapter2"
TAB = DELIV / "assets" / "tables" / "chapter2"
FIG.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

for font_path in [
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path(r"C:\Windows\Fonts\simsun.ttc"),
]:
    if font_path.exists():
        font_manager.fontManager.addfont(str(font_path))

FONT_FAMILY = [
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "Noto Sans CJK SC",
    "Segoe UI",
    "DejaVu Sans",
    "Arial",
    "sans-serif",
]
plt.rcParams["font.sans-serif"] = FONT_FAMILY
plt.rcParams["axes.unicode_minus"] = False

TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
}
COLORS = {
    "blue": {"base": "#A3BEFA", "mid": "#5477C4", "dark": "#2E4780", "light": "#CEDFFE", "xlight": "#EAF1FE"},
    "gold": {"base": "#FFE15B", "mid": "#B8A037", "dark": "#736422", "light": "#FFEA8F", "xlight": "#FFF4C2"},
    "orange": {"base": "#F0986E", "mid": "#CC6F47", "dark": "#804126", "light": "#FFBDA1", "xlight": "#FFEDDE"},
    "olive": {"base": "#A3D576", "mid": "#71B436", "dark": "#386411", "light": "#BEEB96", "xlight": "#D8ECBD"},
    "pink": {"base": "#F390CA", "mid": "#BD569B", "dark": "#8A3A6F", "light": "#F5BACC", "xlight": "#FCDAD6"},
    "neutral": {"base": "#C5CAD3", "mid": "#7A828F", "dark": "#464C55", "light": "#E2E5EA", "xlight": "#F4F5F7"},
}


def apply_theme() -> None:
    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.facecolor": TOKENS["surface"],
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "grid.color": TOKENS["grid"],
            "axes.labelcolor": TOKENS["ink"],
            "xtick.color": TOKENS["muted"],
            "ytick.color": TOKENS["muted"],
            "font.sans-serif": FONT_FAMILY,
            "font.family": "sans-serif",
        },
    )


def header(fig, ax, title: str, subtitle: str, top: float = 0.88) -> None:
    ax.set_title("")
    fig.subplots_adjust(top=top)
    left = ax.get_position().x0
    fig.text(left, 0.985, title, ha="left", va="top", fontsize=15, fontweight="semibold", color=TOKENS["ink"])
    fig.text(left, 0.94, subtitle, ha="left", va="top", fontsize=9.5, color=TOKENS["muted"])
    sns.despine(ax=ax)


def save(fig, name: str) -> None:
    fig.savefig(FIG / f"{name}.png", dpi=220, bbox_inches="tight", facecolor=TOKENS["surface"])
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight", facecolor=TOKENS["surface"])
    plt.close(fig)


def build_asset_tables_and_charts() -> None:
    config = json.loads((MVP / "config.json").read_text(encoding="utf-8"))
    etfs = config["sector_etfs"]
    asset_rows = [
        {"代码": "510150.SH", "简称": "招商消费ETF", "行业暴露": "消费", "选择依据": "内需与消费风格代表，成立较早"},
        {"代码": "510170.SH", "简称": "国联安大宗商品ETF", "行业暴露": "商品/资源", "选择依据": "资源品与商品周期代表"},
        {"代码": "510230.SH", "简称": "国泰金融ETF", "行业暴露": "金融", "选择依据": "金融周期与大盘价值风格代表"},
        {"代码": "159929.SZ", "简称": "汇添富医药ETF", "行业暴露": "医药", "选择依据": "防御与成长属性兼具"},
        {"代码": "159930.SZ", "简称": "汇添富能源ETF", "行业暴露": "能源", "选择依据": "能源价格与周期风险暴露"},
        {"代码": "512330.SH", "简称": "南方信息科技ETF", "行业暴露": "信息技术", "选择依据": "科技成长风格代表"},
    ]
    asset_df = pd.DataFrame(asset_rows)
    asset_df.to_csv(TAB / "chapter2_asset_pool.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(12.5, 6.8))
    ax.axis("off")
    palette = [COLORS["blue"], COLORS["gold"], COLORS["orange"], COLORS["olive"], COLORS["pink"], COLORS["neutral"]]
    for i, row in asset_df.iterrows():
        col = i % 3
        r = i // 3
        x, y = 0.06 + col * 0.31, 0.58 - r * 0.35
        fam = palette[i]
        box = FancyBboxPatch(
            (x, y),
            0.26,
            0.22,
            boxstyle="round,pad=0.018,rounding_size=0.018",
            facecolor=fam["xlight"],
            edgecolor=fam["dark"],
            linewidth=1.2,
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(x + 0.02, y + 0.165, row["行业暴露"], transform=ax.transAxes, fontsize=16, fontweight="bold", color=TOKENS["ink"])
        ax.text(x + 0.02, y + 0.115, row["简称"], transform=ax.transAxes, fontsize=10.5, color=TOKENS["ink"])
        ax.text(x + 0.02, y + 0.075, row["代码"], transform=ax.transAxes, fontsize=10, color=TOKENS["muted"], family="Consolas")
        ax.text(x + 0.02, y + 0.033, textwrap.fill(row["选择依据"], 17), transform=ax.transAxes, fontsize=9.2, color=TOKENS["muted"])
    ax.text(0.06, 0.93, "图2-1 六类宽口径行业 ETF 的经济暴露", transform=ax.transAxes, fontsize=15, fontweight="semibold", color=TOKENS["ink"])
    ax.text(
        0.06,
        0.885,
        "基础资产池覆盖消费、商品/资源、金融、医药、能源和信息技术，用低维横截面保留行业轮动含义。",
        transform=ax.transAxes,
        fontsize=9.5,
        color=TOKENS["muted"],
    )
    save(fig, "fig2_1_etf_industry_coverage")

    prices = pd.read_csv(MVP / "data" / "processed" / "adjusted_close.csv", parse_dates=["date"]).set_index("date")
    symbol_map = {
        "sh510150": "510150.SH",
        "sh510170": "510170.SH",
        "sh510230": "510230.SH",
        "sz159929": "159929.SZ",
        "sz159930": "159930.SZ",
        "sh512330": "512330.SH",
        "sh510300": "510300.SH",
    }
    coverage = []
    for sym, code in symbol_map.items():
        if sym in prices.columns:
            s = prices[sym].dropna()
            coverage.append(
                {
                    "代码": code,
                    "名称": etfs.get(sym, "沪深300ETF"),
                    "数据起点": s.index.min().date().isoformat(),
                    "数据终点": s.index.max().date().isoformat(),
                    "交易日数": len(s),
                }
            )
    coverage_df = pd.DataFrame(coverage)
    coverage_df.to_csv(TAB / "chapter2_data_coverage.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(12.8, 5.8))
    coverage_plot = coverage_df.copy()
    coverage_plot["start"] = pd.to_datetime(coverage_plot["数据起点"])
    coverage_plot["end"] = pd.to_datetime(coverage_plot["数据终点"])
    coverage_plot["label"] = coverage_plot["名称"].str.replace("ETF", "ETF ", regex=False) + "(" + coverage_plot["代码"] + ")"
    coverage_plot = coverage_plot.sort_values("start", ascending=False)
    for i, (_, row) in enumerate(coverage_plot.iterrows()):
        color = COLORS["blue"]["base"] if row["代码"] != "510300.SH" else COLORS["neutral"]["base"]
        edge = COLORS["blue"]["dark"] if row["代码"] != "510300.SH" else COLORS["neutral"]["dark"]
        ax.barh(i, (row["end"] - row["start"]).days, left=row["start"], height=0.56, color=color, edgecolor=edge, linewidth=1.0)
        ax.text(row["start"], i + 0.32, row["数据起点"], fontsize=8.5, color=TOKENS["muted"], va="bottom")
    ax.set_yticks(np.arange(len(coverage_plot)), coverage_plot["label"])
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlabel("日频价格样本区间")
    ax.set_ylabel("")
    header(fig, ax, "图2-2 基础资产池的数据覆盖时间线", "公开日频价格覆盖至 2026-06-18；共同样本长度决定训练窗口和第一版回测起点。")
    save(fig, "fig2_2_data_coverage_timeline")


def build_factor_charts() -> None:
    factor_rows = [
        {"因子": "季度动量", "变量": "mom_63", "窗口": "63个交易日", "计算方式": "当前价格 / 63日前价格 - 1", "经济含义": "近一季度相对强弱", "预期方向": "越高越强"},
        {"因子": "半年动量", "变量": "mom_126", "窗口": "126个交易日", "计算方式": "当前价格 / 126日前价格 - 1", "经济含义": "中期趋势延续", "预期方向": "越高越强"},
        {"因子": "一年动量", "变量": "mom_252", "窗口": "252个交易日", "计算方式": "当前价格 / 252日前价格 - 1", "经济含义": "长周期行业强弱", "预期方向": "越高越强"},
        {"因子": "趋势质量", "变量": "trend_quality_126", "窗口": "126个交易日", "计算方式": "对数价格滚动趋势拟合质量", "经济含义": "区分平滑趋势与单点跳涨", "预期方向": "越高越稳定"},
        {"因子": "低波动", "变量": "low_vol_63", "窗口": "63个交易日", "计算方式": "- 年化滚动波动率", "经济含义": "短期风险稳定性", "预期方向": "越高表示波动越低"},
    ]
    factor_df = pd.DataFrame(factor_rows)
    factor_df.to_csv(TAB / "chapter2_factor_definitions.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(12.8, 5.6))
    ax.axis("off")
    stages = [
        ("价格序列", "ETF 日频复权价格"),
        ("收益与窗口", "63 / 126 / 252 日滚动计算"),
        ("量价因子", "动量、趋势质量、低波动"),
        ("横截面标准化", "同一调仓日不同 ETF 可比"),
        ("排序信号", "输入正则化模型形成相对分数"),
    ]
    for i, (title, sub) in enumerate(stages):
        x = 0.04 + i * 0.19
        box = FancyBboxPatch(
            (x, 0.42),
            0.15,
            0.22,
            boxstyle="round,pad=0.018,rounding_size=0.014",
            facecolor=COLORS["gold"]["xlight"] if i < 3 else COLORS["blue"]["xlight"],
            edgecolor=COLORS["gold"]["dark"] if i < 3 else COLORS["blue"]["dark"],
            linewidth=1.1,
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(x + 0.075, 0.56, title, ha="center", va="center", fontsize=13, fontweight="semibold", color=TOKENS["ink"], transform=ax.transAxes)
        ax.text(x + 0.075, 0.48, textwrap.fill(sub, 14), ha="center", va="center", fontsize=9, color=TOKENS["muted"], transform=ax.transAxes)
        if i < len(stages) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x + 0.155, 0.53),
                    (x + 0.185, 0.53),
                    arrowstyle="-|>",
                    mutation_scale=14,
                    linewidth=1.2,
                    color=COLORS["neutral"]["dark"],
                    transform=ax.transAxes,
                )
            )
    rng = np.random.default_rng(1)
    xx = np.linspace(0.05, 0.18, 60)
    yy = 0.22 + np.cumsum(rng.normal(0, 0.004, 60)) + np.linspace(0, 0.07, 60)
    ax.plot(xx, yy, color=COLORS["blue"]["mid"], linewidth=1.5, transform=ax.transAxes)
    ax.text(0.04, 0.82, "图2-3 初始因子从价格序列到排序信号的构造路径", fontsize=15, fontweight="semibold", color=TOKENS["ink"], transform=ax.transAxes)
    ax.text(0.04, 0.765, "初始五因子不是最终筛选结果，而是用于建立第一版机器学习轮动框架的量价基准信号。", fontsize=9.5, color=TOKENS["muted"], transform=ax.transAxes)
    save(fig, "fig2_3_factor_construction_schematic")

    panel = pd.read_csv(MVP / "data" / "processed" / "monthly_feature_panel.csv", parse_dates=["date"])
    fcols = ["mom_63", "mom_126", "mom_252", "trend_quality_126", "low_vol_63"]
    label_map = {
        "mom_63": "季度动量",
        "mom_126": "半年动量",
        "mom_252": "一年动量",
        "trend_quality_126": "趋势质量",
        "low_vol_63": "低波动",
    }
    corr = panel[fcols].dropna().corr().rename(index=label_map, columns=label_map)
    corr.to_csv(TAB / "chapter2_initial_factor_correlation.csv", encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(8.8, 7.4))
    cmap = sns.blend_palette(["#FFFFFF", COLORS["blue"]["xlight"], COLORS["blue"]["base"], COLORS["blue"]["dark"]], as_cmap=True)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap=cmap, vmin=-1, vmax=1, linewidths=1, linecolor="#FFFFFF", cbar_kws={"label": "相关系数"}, ax=ax)
    ax.tick_params(axis="x", labelrotation=0)
    ax.tick_params(axis="y", labelrotation=0)
    header(fig, ax, "图2-4 初始五因子的相关性矩阵", "动量类因子相关性较高，说明第一版信号已经存在共线性，后续需要因子治理而不是单纯扩张变量。", top=0.84)
    save(fig, "fig2_4_initial_factor_correlation")


def build_strategy_and_result_charts() -> None:
    params_df = pd.DataFrame(
        [
            {"模块": "资产池", "第一版设定": "六类宽口径行业 ETF", "含义": "控制横截面维度，保留行业轮动含义"},
            {"模块": "因子组", "第一版设定": "季度动量、半年动量、一年动量、趋势质量、低波动", "含义": "用量价变量刻画行业状态"},
            {"模块": "模型", "第一版设定": "Ridge / LASSO 正则化排序，并保留固定因子合成作对照", "含义": "比较机器学习排序与简单合成信号"},
            {"模块": "训练窗口", "第一版设定": "滚动训练；最少60个月历史样本", "含义": "只使用信号日前可见数据"},
            {"模块": "调仓规则", "第一版设定": "月度信号，Top-K=3", "含义": "低频轮动，避免高频噪声"},
            {"模块": "权重规则", "第一版设定": "入选 ETF 等权或反波动率配置", "含义": "机器学习不直接输出仓位比例"},
            {"模块": "执行与成本", "第一版设定": "T+1执行，单边成本15bp", "含义": "约束回测可交易性"},
        ]
    )
    params_df.to_csv(TAB / "chapter2_strategy_params.csv", index=False, encoding="utf-8-sig")

    label_names = {
        "Ridge walk-forward": "Ridge 正则化排序策略",
        "Lasso walk-forward": "LASSO 正则化排序策略",
        "Fixed composite": "固定因子合成策略",
        "CSI 300 ETF": "沪深300ETF",
        "Equal-weight sectors": "行业ETF买入并持有等权基准",
    }
    equity = pd.read_csv(MVP / "outputs" / "daily_equity.csv", parse_dates=["date"]).set_index("date").rename(columns=label_names)
    series_order = list(label_names.values())
    line_colors = [COLORS["blue"]["mid"], COLORS["orange"]["mid"], COLORS["gold"]["mid"], COLORS["neutral"]["mid"], COLORS["olive"]["mid"]]

    fig, ax = plt.subplots(figsize=(12.8, 6.8))
    for col, color in zip(series_order, line_colors):
        if col in equity.columns:
            ax.plot(equity.index, equity[col], label=col, linewidth=1.35, color=color)
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.1f}"))
    ax.set_xlabel("")
    ax.set_ylabel("累计净值（起点=1）")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=3, frameon=False, fontsize=9)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    header(fig, ax, "图2-7 第一版基准策略累计净值", "2020-09-21 至 2026-06-18；单边成本15bp。正则化排序策略与简单因子合成均跑通，但这里只作为后续优化参照。", top=0.82)
    save(fig, "fig2_7_baseline_equity_curves")

    fig, ax = plt.subplots(figsize=(12.8, 6.5))
    dd = equity / equity.cummax() - 1
    for col, color in zip(series_order, line_colors):
        if col in dd.columns:
            ax.plot(dd.index, dd[col], label=col, linewidth=1.2, color=color)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_xlabel("")
    ax.set_ylabel("相对历史峰值回撤")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=3, frameon=False, fontsize=9)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    header(fig, ax, "图2-8 第一版基准策略回撤路径", "回撤按“当前累计净值 / 历史最高累计净值 - 1”计算；正则化排序并不能消除回撤，趋势约束和市场状态仍然关键。", top=0.82)
    save(fig, "fig2_8_baseline_drawdowns")

    fig, ax = plt.subplots(figsize=(12.8, 6.2))
    focal = "Ridge 正则化排序策略"
    benchmarks = ["沪深300ETF", "行业ETF买入并持有等权基准"]
    colors = [COLORS["blue"]["mid"], COLORS["olive"]["mid"]]
    for b, c in zip(benchmarks, colors):
        ex = equity[focal] / equity[b] - 1
        ax.plot(ex.index, ex, label=f"相对{b}", linewidth=1.35, color=c)
    ax.axhline(0, color=TOKENS["ink"], linewidth=1, linestyle=":")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_xlabel("")
    ax.set_ylabel("累计超额收益")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=2, frameon=False, fontsize=9)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    header(fig, ax, "图2-9 Ridge 排序策略相对主要基准的累计超额", "超额收益按策略净值相对基准净值的比例变化计算；用于说明第一版排序流程是否相对朴素配置产生增量。", top=0.84)
    save(fig, "fig2_9_baseline_excess_returns")

    metrics = pd.read_csv(MVP / "outputs" / "metrics.csv")
    first_metrics = metrics[metrics["period"].eq("full_walk_forward")].copy()
    first_metrics["策略"] = first_metrics["strategy"].map(label_names).fillna(first_metrics["strategy"])
    metric_out = first_metrics[
        ["策略", "start", "end", "cagr", "sharpe", "max_drawdown", "calmar", "monthly_win_rate", "annual_gross_turnover"]
    ].rename(
        columns={
            "start": "起始日",
            "end": "结束日",
            "cagr": "CAGR",
            "sharpe": "Sharpe",
            "max_drawdown": "最大回撤",
            "calmar": "Calmar",
            "monthly_win_rate": "月度胜率",
            "annual_gross_turnover": "年化总权重交易量",
        }
    )
    metric_out.to_csv(TAB / "chapter2_first_backtest_metrics.csv", index=False, encoding="utf-8-sig")

    comp = pd.read_csv(DELIV / "assets" / "tables" / "component_ablation.csv")
    comp_label = {
        "ranking_only": "仅因子排序",
        "ranking_plus_trend": "排序 + 趋势过滤",
        "ranking_plus_inverse_vol": "排序 + 反波动率权重",
        "complete_base": "完整基准策略",
        "complete_plus_amount": "完整策略 + 成交额因子",
    }
    comp_full = comp[comp["period"].eq("full_walk_forward")].copy()
    comp_full["版本"] = comp_full["component"].map(comp_label)
    comp_full.to_csv(TAB / "chapter2_component_ablation.csv", index=False, encoding="utf-8-sig")

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.8), sharey=True)
    plot_df = comp_full.sort_values("sharpe", ascending=True)
    bar_colors = [COLORS["blue"]["base"] if v == "完整基准策略" else COLORS["neutral"]["light"] for v in plot_df["版本"]]
    axes[0].barh(plot_df["版本"], plot_df["sharpe"], color=bar_colors, edgecolor=COLORS["neutral"]["dark"], linewidth=1)
    axes[0].set_xlabel("Sharpe")
    axes[0].set_ylabel("")
    axes[0].axvline(0, color=TOKENS["ink"], linewidth=1, linestyle=":")

    plot_df2 = comp_full.sort_values("max_drawdown", ascending=True)
    bar_colors2 = [COLORS["orange"]["base"] if v == "仅因子排序" else COLORS["neutral"]["light"] for v in plot_df2["版本"]]
    axes[1].barh(plot_df2["版本"], plot_df2["max_drawdown"], color=bar_colors2, edgecolor=COLORS["neutral"]["dark"], linewidth=1)
    axes[1].set_xlabel("最大回撤")
    axes[1].xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    for ax_ in axes:
        ax_.grid(True, axis="x")
        ax_.grid(False, axis="y")
    fig.subplots_adjust(top=0.78, wspace=0.24)
    fig.text(0.08, 0.97, "图2-10 基准策略收益来源的组件拆解", fontsize=15, fontweight="semibold", color=TOKENS["ink"], ha="left", va="top")
    fig.text(0.08, 0.915, "2020-10-12 至 2026-06-18。仅排序版本表现较弱；加入趋势过滤后，风险收益和回撤均明显改善。", fontsize=9.5, color=TOKENS["muted"], ha="left", va="top")
    sns.despine(fig=fig)
    save(fig, "fig2_10_component_ablation_metrics")


def build_chart_map() -> None:
    chart_map = pd.DataFrame(
        [
            {"图号": "图2-1", "文件": "assets/figures/chapter2/fig2_1_etf_industry_coverage.png", "用途": "展示基础资产池行业覆盖"},
            {"图号": "图2-2", "文件": "assets/figures/chapter2/fig2_2_data_coverage_timeline.png", "用途": "展示样本覆盖和共同样本约束"},
            {"图号": "图2-3", "文件": "assets/figures/chapter2/fig2_3_factor_construction_schematic.png", "用途": "解释初始因子构造"},
            {"图号": "图2-4", "文件": "assets/figures/chapter2/fig2_4_initial_factor_correlation.png", "用途": "展示初始因子共线性"},
            {"图号": "图2-5", "文件": "正文 Mermaid 图", "用途": "解释基准策略流程"},
            {"图号": "图2-6", "文件": "正文 Mermaid 图", "用途": "解释训练窗口和T+1执行"},
            {"图号": "图2-7", "文件": "assets/figures/chapter2/fig2_7_baseline_equity_curves.png", "用途": "展示第一版累计净值"},
            {"图号": "图2-8", "文件": "assets/figures/chapter2/fig2_8_baseline_drawdowns.png", "用途": "展示第一版回撤"},
            {"图号": "图2-9", "文件": "assets/figures/chapter2/fig2_9_baseline_excess_returns.png", "用途": "展示相对基准累计超额"},
            {"图号": "图2-10", "文件": "assets/figures/chapter2/fig2_10_component_ablation_metrics.png", "用途": "展示收益来源拆解"},
        ]
    )
    chart_map.to_csv(TAB / "chapter2_chart_map.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    apply_theme()
    build_asset_tables_and_charts()
    build_factor_charts()
    build_strategy_and_result_charts()
    build_chart_map()
    print(f"Chapter 2 assets generated under: {FIG}")


if __name__ == "__main__":
    main()
