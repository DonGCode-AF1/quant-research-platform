# -*- coding: utf-8 -*-
"""Create contact sheets for existing exploration figures."""

from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "figures" / "_audit"
OUT.mkdir(parents=True, exist_ok=True)

FIGURES = [
    ("资产池：6/8对比", r"mvp_cn\outputs\final_report\figures\8etf_vs_6etf_comparison.png"),
    ("资产池：颗粒度摘要", r"mvp_cn\outputs\final_report\figures\04_granularity_summary.png"),
    ("8ETF扩展：净值", r"mvp_cn\outputs\eight_etf_extended\figures\equity_comparison.png"),
    ("8ETF扩展：指标热力", r"mvp_cn\outputs\eight_etf_extended\figures\post2023_metric_heatmap.png"),
    ("因子：IC与冗余", r"mvp_cn\outputs\factor_candidates\candidate_ic_vs_redundancy.png"),
    ("因子：分期IC热力", r"mvp_cn\outputs\factor_candidates\candidate_subperiod_ic_heatmap.png"),
    ("因子：管线结果", r"mvp_cn\outputs\final_report\figures\factor_pipeline_final.png"),
    ("LASSO/Ridge/POOS", r"mvp_cn\outputs\final_report\figures\lasso_ridge_poos.png"),
    ("模型：净值对比", r"mvp_cn\outputs\model_comparison\figures\main_equity_comparison.png"),
    ("模型：指标对比", r"mvp_cn\outputs\model_comparison\figures\main_metric_comparison.png"),
    ("模型：训练窗口", r"mvp_cn\outputs\model_comparison\figures\training_window_sharpe.png"),
    ("二轮：训练窗口净值", r"mvp_cn\outputs\second_round\figures\training_windows_equity.png"),
    ("频率：成本后净值", r"mvp_cn\outputs\second_round\figures\frequency_equity_15bp.png"),
    ("高频：Sharpe热力", r"mvp_cn\outputs\high_freq_adaptive\figures\sharpe_heatmap.png"),
    ("180MA：选择过程", r"mvp_cn\outputs\ma180_final\figures\ma_selection_process.png"),
    ("180MA：原因解释", r"mvp_cn\outputs\ma180_final\figures\why_180_beats_200.png"),
    ("最终：关键版本", r"quant-research-platform\projects\final-classroom-delivery\assets\figures\deep_key_version_comparison.png"),
    ("最终：90组摘要", r"quant-research-platform\projects\final-classroom-delivery\assets\figures\deep_final_90_spec_summary.png"),
]


def font(size=28):
    for p in [Path("C:/Windows/Fonts/msyh.ttc"), Path("C:/Windows/Fonts/simhei.ttf")]:
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def main():
    project = Path(r"D:\GProjects\期末量化分析")
    tile_w, tile_h = 520, 340
    label_h = 54
    cols = 3
    rows = (len(FIGURES) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w, rows * (tile_h + label_h)), "#FBFAF6")
    draw = ImageDraw.Draw(sheet)
    fnt = font(24)
    small = font(18)
    for idx, (label, rel) in enumerate(FIGURES):
        path = project / rel
        x = (idx % cols) * tile_w
        y = (idx // cols) * (tile_h + label_h)
        draw.rectangle([x, y, x + tile_w, y + label_h], fill="#EFE8DC")
        draw.text((x + 16, y + 12), label, fill="#102A43", font=fnt)
        if not path.exists():
            draw.text((x + 16, y + label_h + 120), "missing", fill="#A33A3A", font=fnt)
            continue
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((tile_w - 28, tile_h - 24), Image.LANCZOS)
            canvas = Image.new("RGB", (tile_w, tile_h), "white")
            canvas.paste(img, ((tile_w - img.width) // 2, (tile_h - img.height) // 2))
            sheet.paste(canvas, (x, y + label_h))
        except Exception as e:
            draw.text((x + 16, y + label_h + 80), str(e)[:45], fill="#A33A3A", font=small)
    out = OUT / "existing_visuals_contact_sheet.png"
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
