# 课堂展示交付入口

## 可直接查看

- `index.html`：课堂展示 HTML 网页版。
- `final_classroom_delivery.pptx`：课堂备用 PPTX。
- `validation_results_report.html`：策略检验结果整合报告，用于继续并入原有汇报框架。

## 渲染前源文件

- `source/final_narrative_draft.md`：人工修订优先使用的完整文稿源文件。
- `source/classroom_report_body.md`：用于 HTML 渲染的正文版本，去除了手写目录。
- `source/index.qmd`：Quarto 包装文件。
- `source/slides.qmd`：RevealJS 幻灯片源文件。
- `source/speaker_notes.md`：逐页讲稿。
- `source/references.bib`：参考文献。
- `source/supplement_rotation_and_model_questions.md`：月度持仓、LASSO/Ridge、ETF 池选择和轮动关系补充说明。
- `source/supplement_training_window_sensitivity.md`：训练窗口敏感性与稳健性补充说明。
- `source/supplement_overfit_diagnostics.md`：规格搜索过拟合风险与 60 个月训练窗口坍塌检查。
- `source/final_strategy_validation_audit.md`：最终策略检验覆盖矩阵、策略清单与指标审计。
- `source/standard_quant_research_process_audit.md`：按规范量化研究流程重新审视研究过程与有效性边界。
- `source/validation_results_report.qmd`：策略检验结果整合报告源文件。

## 发布说明

如果 GitHub Pages 使用 `main` 分支的 `docs/` 目录发布，则网页链接为：

`https://dongcode-af1.github.io/quant-research-platform/classroom-report/`

如果仓库 Pages 尚未启用，需要在 GitHub 仓库 Settings -> Pages 中选择 `Deploy from a branch`，分支为 `main`，目录为 `/docs`。
