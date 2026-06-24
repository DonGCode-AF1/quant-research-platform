# 课堂展示交付入口

## 可直接查看

- `index.html`：课堂展示 HTML 网页版。
- `final_classroom_delivery.pptx`：课堂备用 PPTX。

## 渲染前源稿

- `source/final_narrative_draft.md`：人工修订优先使用的完整文稿源文件。
- `source/classroom_report_body.md`：用于 HTML 渲染的正文版本，去除了手写目录。
- `source/index.qmd`：Quarto 包装文件。
- `source/slides.qmd`：RevealJS 幻灯片源文件。
- `source/speaker_notes.md`：逐页讲稿。
- `source/references.bib`：参考文献。

## 发布说明

若 GitHub Pages 使用 `main` 分支的 `docs/` 目录发布，则网页链接为：

`https://dongcode-af1.github.io/quant-research-platform/classroom-report/`

如果仓库 Pages 尚未启用，需要在 GitHub 仓库 Settings -> Pages 中选择 `Deploy from a branch`，分支为 `main`，目录为 `/docs`。
