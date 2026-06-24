# -*- coding: utf-8 -*-
"""Build a decision-style workflow diagram for the ETF rotation project."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def setup_font() -> None:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]
    for path in candidates:
        if path.exists():
            font_manager.fontManager.addfont(str(path))
            plt.rcParams["font.family"] = font_manager.FontProperties(fname=str(path)).get_name()
            break
    plt.rcParams["axes.unicode_minus"] = False


def draw_box(ax, xy, text, width=2.15, height=0.74, fc="#F7F3EA", ec="#16324F", lw=1.45, fontsize=11.6):
    x, y = xy
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.025,rounding_size=0.035",
        linewidth=lw,
        facecolor=fc,
        edgecolor=ec,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color="#102A43", linespacing=1.25)
    return patch


def draw_diamond(ax, xy, text, width=2.45, height=1.05, fc="#FFF8E6", ec="#9B6B22", lw=1.55, fontsize=11.1):
    x, y = xy
    pts = [(x, y + height / 2), (x + width / 2, y), (x, y - height / 2), (x - width / 2, y)]
    patch = Polygon(pts, closed=True, linewidth=lw, facecolor=fc, edgecolor=ec)
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color="#102A43", linespacing=1.22)
    return patch


def arrow(ax, start, end, text=None, rad=0.0, color="#5C6F82", lw=1.55, shrink=8):
    arr = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=lw,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=shrink,
        shrinkB=shrink,
    )
    ax.add_patch(arr)
    if text:
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ax.text(
            mx,
            my + (0.18 if rad == 0 else 0.35 * (1 if rad > 0 else -1)),
            text,
            ha="center",
            va="center",
            fontsize=10.2,
            color=color,
            bbox=dict(boxstyle="round,pad=0.18", facecolor="#FBFAF6", edgecolor="none", alpha=0.9),
        )
    return arr


def elbow_arrow(ax, points, color="#A33A3A", lw=1.55, text=None):
    for idx in range(len(points) - 1):
        arrow(
            ax,
            points[idx],
            points[idx + 1],
            color=color,
            lw=lw,
            shrink=0 if idx < len(points) - 2 else 8,
        )
    if text:
        x, y = points[len(points) // 2]
        ax.text(
            x,
            y + 0.18,
            text,
            ha="center",
            va="center",
            fontsize=10.2,
            color=color,
            bbox=dict(boxstyle="round,pad=0.18", facecolor="#FBFAF6", edgecolor="none", alpha=0.9),
        )


def build():
    setup_font()
    fig, ax = plt.subplots(figsize=(21, 11.2), dpi=220)
    fig.patch.set_facecolor("#FBFAF6")
    ax.set_facecolor("#FBFAF6")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9.4)
    ax.axis("off")

    ax.text(
        0.55,
        8.9,
        "行业 ETF 轮动研究的操作逻辑闭环",
        fontsize=24,
        weight="bold",
        color="#102A43",
        ha="left",
        va="center",
    )
    ax.text(
        0.57,
        8.47,
        "矩形表示处理步骤，菱形表示审查判断；判断不通过时回到相应环节重新设计，避免把单次回测结果直接当作结论。",
        fontsize=12.2,
        color="#52616B",
        ha="left",
        va="center",
    )

    # Main construction path
    top_y = 7.18
    xs = [1.35, 3.85, 6.35, 8.85, 11.35, 13.85]
    draw_box(ax, (xs[0], top_y), "研究问题界定\n行业轮动\n低频配置", fc="#EAF2F8")
    draw_box(ax, (xs[1], top_y), "数据与资产池\n日频价格与成交\nETF口径", fc="#EAF2F8")
    draw_box(ax, (xs[2], top_y), "因子构造\n动量\n趋势质量\n波动", fc="#EAF2F8")
    draw_box(ax, (xs[3], top_y), "正则化排序\nRidge\nLASSO\nElastic Net", fc="#EAF2F8")
    draw_box(ax, (xs[4], top_y), "组合与交易\n趋势过滤\nTop-K / T+1\n成本约束", fc="#EAF2F8")
    draw_box(ax, (xs[5], top_y), "回测输出\n净值与回撤\n换手与超额", fc="#EAF2F8")

    for a, b in [
        ((2.42, top_y), (2.78, top_y)),
        ((4.92, top_y), (5.28, top_y)),
        ((7.42, top_y), (7.78, top_y)),
        ((9.92, top_y), (10.28, top_y)),
        ((12.42, top_y), (12.78, top_y)),
    ]:
        arrow(ax, a, b)

    # Review path
    draw_diamond(ax, (13.85, 5.55), "是否显著优于\n主要基准？")
    draw_diamond(ax, (11.1, 4.25), "是否存在明显\n规格搜索风险？")
    draw_diamond(ax, (8.15, 4.25), "伪样本外\n切分检验\n是否稳定？", width=2.55)
    draw_diamond(ax, (5.2, 4.25), "机制是否可解释？\n趋势、排序\n风险暴露", width=2.55)

    arrow(ax, (13.85, 6.7), (13.85, 6.12), "进入审查")
    arrow(ax, (13.0, 5.32), (12.15, 4.67), "是")
    arrow(ax, (9.82, 4.25), (9.45, 4.25), "可控")
    arrow(ax, (6.72, 4.25), (6.48, 4.25), "稳定")

    draw_box(ax, (2.35, 4.25), "结果解释\n机器学习作用\n策略性质", fc="#E8F3EE")
    arrow(ax, (3.42, 4.25), (3.92, 4.25))

    draw_box(ax, (2.35, 2.5), "最终呈现\n策略口径\n证据与限制", fc="#DDEBEA", ec="#2F6F63", width=2.35)
    arrow(ax, (2.35, 3.82), (2.35, 2.97))

    # Iteration loop nodes
    draw_box(ax, (4.75, 1.55), "重新设计资产池\n宽口径 / 细分 / 扩容", fc="#F8EDEB", ec="#A33A3A")
    draw_box(ax, (7.35, 1.55), "治理候选因子\n相关性 / IC\nLASSO筛选", fc="#F8EDEB", ec="#A33A3A")
    draw_box(ax, (9.95, 1.55), "调整模型与窗口\n5年 / 8年\n扩展窗口", fc="#F8EDEB", ec="#A33A3A")
    draw_box(ax, (12.55, 1.55), "修正交易规则\n频率 / 调仓日\n均线长度", fc="#F8EDEB", ec="#A33A3A")

    arrow(ax, (13.85, 5.0), (13.15, 2.1), "否", rad=-0.08)
    arrow(ax, (11.1, 3.7), (10.35, 2.1), "风险偏高", rad=-0.05)
    arrow(ax, (8.15, 3.7), (7.6, 2.1), "不稳定", rad=-0.05)
    arrow(ax, (5.2, 3.7), (4.9, 2.1), "解释不足", rad=-0.05)

    arrow(ax, (5.82, 1.55), (6.28, 1.55))
    arrow(ax, (8.42, 1.55), (8.88, 1.55))
    arrow(ax, (11.02, 1.55), (11.48, 1.55))
    elbow_arrow(
        ax,
        [(13.65, 1.55), (15.15, 1.55), (15.15, 7.95), (3.85, 7.95), (3.85, 7.66)],
        color="#A33A3A",
        text="进入下一轮设计",
    )

    # Legend
    draw_box(ax, (11.5, 8.6), "处理步骤", width=1.28, height=0.42, fc="#EAF2F8", ec="#16324F", lw=1.2, fontsize=10.5)
    draw_diamond(ax, (13.0, 8.6), "判断", width=1.0, height=0.5, fc="#FFF8E6", ec="#9B6B22", lw=1.2, fontsize=10.5)
    draw_box(ax, (14.35, 8.6), "迭代修正", width=1.35, height=0.42, fc="#F8EDEB", ec="#A33A3A", lw=1.2, fontsize=10.5)

    out_png = OUT_DIR / "operation_logic_cycle_flowchart.png"
    out_svg = OUT_DIR / "operation_logic_cycle_flowchart.svg"
    out_mcp_png = OUT_DIR / "operation_logic_cycle_flowchart_mcp.png"
    out_mcp_svg = OUT_DIR / "operation_logic_cycle_flowchart_mcp.svg"
    for out in (out_png, out_svg, out_mcp_png, out_mcp_svg):
        fig.savefig(out, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(out_png)
    print(out_svg)
    print(out_mcp_png)
    print(out_mcp_svg)


if __name__ == "__main__":
    build()
