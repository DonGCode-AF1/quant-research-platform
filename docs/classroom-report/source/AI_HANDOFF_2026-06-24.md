# AI 接手说明：课堂展示交付与网页发布

更新时间：2026-06-24 晚  
主目录：`D:\GProjects\期末量化分析\quant-research-platform\projects\final-classroom-delivery`

## 1. 当前交付状态

本轮工作目标是把行业 ETF 轮动研究整理成可展示、可人工修订、可发布的课堂交付物。当前已经形成三类产物：

- 网页报告：`classroom_report.html`
- 渲染前源稿：`final_narrative_draft.md`
- 发布副本：`D:\GProjects\期末量化分析\quant-research-platform\docs\classroom-report\`

GitHub Pages 发布路径已准备为：

`https://dongcode-af1.github.io/quant-research-platform/classroom-report/`

注意：本地 Git 仓库位于 `quant-research-platform` 子目录，而不是外层 `D:\GProjects\期末量化分析`。外层 `.git` 不构成有效仓库。

## 2. 权威文件关系

### 2.1 人工修订优先文件

`final_narrative_draft.md`

这是最重要的正文源稿。用户如果继续人工改文，应优先改这个文件。正文结构、章节标题、段落、图表引用都以它为准。

### 2.2 HTML 渲染正文

`classroom_report_body.md`

这是从 `final_narrative_draft.md` 派生的网页正文版本。它去掉了手写目录，并给标题、副标题、引言加了 `.unlisted`，避免进入目录。

如果用户改了 `final_narrative_draft.md`，后续 AI 应同步更新 `classroom_report_body.md`，再重新生成 HTML。

### 2.3 Quarto 包装文件

`index.qmd`

用于 Quarto HTML 渲染的包装文件。当前已修复中文元数据：

- title: `机器学习辅助的中国行业 ETF 轮动研究`
- subtitle: `低频配置框架、正则化排序与回测审查`
- css: `report.css`
- include: `classroom_report_body.md`

但本机 Quarto 曾出现 Windows 中文编码污染，导致输出 HTML 元数据乱码。因此最终可查看 HTML 当前采用 Pandoc fallback 生成，再人工插入目录块。

### 2.4 样式文件

`report.css`

当前已经重写，修复了此前 `目录` 字样乱码的问题，并为 Pandoc 本地 HTML 适配了正文宽度、目录卡片、图表、表格、标题层级。

关键设计：

- 温暖纸色背景：`--paper: #f7f3ea`
- 深蓝正文与标题：`--ink: #162b3d`
- 暗红强调色：`--accent: #8c3f45`
- 目录块：`#TOC` 与 `body > nav#TOC`
- 目录标题使用 CSS Unicode：`content: "\76EE\5F55";`

### 2.5 发布目录

`docs/classroom-report/`

这是 GitHub Pages 发布副本。当前包含：

- `index.html`：由 `classroom_report.html` 复制而来
- `report.css`
- `assets/`
- `final_classroom_delivery.pptx`
- `source/final_narrative_draft.md`
- `source/classroom_report_body.md`
- `source/index.qmd`
- `source/slides.qmd`
- `source/speaker_notes.md`
- `source/references.bib`

如果修改了项目主目录里的最终文件，需要同步复制到 `docs/classroom-report/`。

## 3. 今天的重要迭代过程

### 3.1 叙事结构重排

用户多次指出早期版本结构混乱、标题不专业、迭代流程没有被合理吸收。后续调整方向是：

- 不把“探索过程”作为流水账直接写在明面上；
- 让章节安排体现研究者如何逐步优化策略；
- 把流程跑通和后续优化区分开；
- 先呈现基准框架与基准结果，再讨论资产池、因子、模型、交易规则优化；
- 将“等权/朴素集成”从“破防时刻”改为规范表达：朴素因子集成的启发；
- 删除“6ETF 等权”等容易误导的口语化说法，改成“基础资产池静态配置基准”等展示口径。

当前正文大章为：

1. 研究问题、资产选择与理论定位
2. 基准策略框架：资产池、因子与排序规则
3. 策略迭代：资产池、因子、模型与交易规则
4. 策略表现与稳健性审查
5. 机制解释与研究启示
6. 局限与后续方向

### 3.2 图表风格迭代

用户指出早期图表“Low”“单调”“表头口语化”“标签不规范”。后续重做方向：

- 不使用内部文件名或实验变量名作为图题；
- 图表标题改成展示型中文标签；
- 表头尽量规范，比如 CAGR、Sharpe、最大回撤、Calmar、胜率、换手率；
- 配色统一为深蓝、暗红、金色、灰绿；
- 图表尽量做成信息面板，而不是简单条形图。

主要图表生成脚本在：

- `tools/build_chapter2_assets.py`
- `tools/build_chapter3_assets.py`
- `tools/build_chapter4_assets.py`
- `tools/build_chapter5_assets.py`
- `tools/build_operation_cycle_flowchart.py`
- `tools/audit_existing_visuals.py`

这些脚本会读取 `assets/tables/` 中的 CSV，并生成 `assets/figures/chapter*/` 下的 PNG/SVG。

### 3.3 目录与 HTML 外观修复

最后一轮用户指出“目录太丑”。处理过程：

1. 检查 `classroom_report.html`，发现 Pandoc 输出没有标准 `<nav id="TOC">`。
2. 检查 `report.css`，发现 `目录` 两字已乱码为 `鐩...`。
3. 重写 `report.css`，修复乱码，并加入 Pandoc 适配样式。
4. 自动扫描 HTML 中 h2/h3 标题，生成正式目录块：
   - 只包含第一章到第六章与小节；
   - 不包含标题、副标题、引言；
   - 目录块插入在标题/副标题之后，引言之前。
5. 将目录样式改为两栏报告式索引卡片：
   - 一级章节加粗；
   - 二级小节弱化；
   - 移动端自动单栏。

## 4. 当前 HTML 生成方法

当前本地最终 HTML 采用 Pandoc：

```powershell
pandoc classroom_report_body.md --standalone --toc --toc-depth=3 --metadata title='机器学习辅助的中国行业 ETF 轮动研究' --metadata lang=zh-CN --css=report.css --include-in-header=html_header.html --mathjax -o classroom_report.html
```

注意：上述命令在当前 Windows shell 中虽然 HTML title 最终可正常显示，但 `--toc` 没有进入模板正文。因此后续还需要运行目录插入脚本逻辑，或者改用定制 Pandoc 模板。

当前使用过的目录插入逻辑是：

1. 读取 `classroom_report.html`
2. 扫描 `<h2>` 和 `<h3>`
3. 跳过 `class="unlisted"` 的标题
4. 生成 `<nav id="TOC" class="report-toc" role="doc-toc">`
5. 插入到引言标题之前

若后续 AI 重新渲染 HTML，需要重新插入目录块，否则页面会没有目录。

## 5. 发布到 GitHub 的当前状态

仓库有效路径：

`D:\GProjects\期末量化分析\quant-research-platform`

远端：

`https://github.com/DonGCode-AF1/quant-research-platform.git`

当前 GitHub CLI 状态：

- `gh auth status` 显示 token invalid；
- 需要用户重新认证：`gh auth login -h github.com`；
- 或者使用已有 Git 凭据直接 `git push`。

本轮已准备的发布文件：

`docs/classroom-report/index.html`

预期 GitHub Pages 链接：

`https://dongcode-af1.github.io/quant-research-platform/classroom-report/`

如果仓库 Pages 没有启用，需要在 GitHub 仓库 Settings -> Pages 中选择：

- Source: Deploy from a branch
- Branch: `main`
- Folder: `/docs`

## 6. 推送前检查清单

推送前应检查：

```powershell
git status --short --branch
```

至少应包含这些新增/修改：

- `docs/.nojekyll`
- `docs/index.md`
- `docs/classroom-report/`
- `projects/final-classroom-delivery/report.css`
- `projects/final-classroom-delivery/index.qmd`
- `projects/final-classroom-delivery/classroom_report.html`
- `projects/final-classroom-delivery/AI_HANDOFF_2026-06-24.md`

检查 HTML 图片：

```powershell
$env:PYTHONIOENCODING='utf-8'
python - <<'PY'
from pathlib import Path
import re
root = Path('docs/classroom-report')
html = (root / 'index.html').read_text(encoding='utf-8')
imgs = re.findall(r'<img[^>]+src="([^"]+)"', html)
missing = [src for src in imgs if not (root / src).exists()]
print(len(imgs), 'images;', len(missing), 'missing')
print(missing[:10])
PY
```

## 7. 后续修改建议

### 7.1 用户要改正文

优先修改：

`projects/final-classroom-delivery/final_narrative_draft.md`

然后同步到：

`projects/final-classroom-delivery/classroom_report_body.md`

最后重新生成：

`projects/final-classroom-delivery/classroom_report.html`

并复制到：

`docs/classroom-report/index.html`

### 7.2 用户要改图表

优先检查正文引用的图表路径，再找对应脚本。

常用对应关系：

- 第二章图表：`tools/build_chapter2_assets.py`
- 第三章图表：`tools/build_chapter3_assets.py`
- 第四章图表：`tools/build_chapter4_assets.py`
- 第五章图表：`tools/build_chapter5_assets.py`
- 流程图：`tools/build_operation_cycle_flowchart.py`

生成后需要确认：

- 图片文件名没有变化，或者同步修改正文引用；
- `docs/classroom-report/assets/` 已同步更新；
- 图表中文标签不使用内部实验变量名；
- 表头使用展示口径，不使用口语标签。

### 7.3 用户要改网页样式

优先修改：

`projects/final-classroom-delivery/report.css`

再复制到：

`docs/classroom-report/report.css`

当前 CSS 同时兼容 Quarto/Pandoc，但最终发布文件是 Pandoc HTML。

## 8. 已知风险

- GitHub CLI token 失效，尚未完成远端推送。
- Quarto 在当前 Windows 环境出现过中文乱码，最终 HTML 暂用 Pandoc fallback。
- `docs/index.md` 已被重写为正常中文入口，原文件此前存在乱码。
- 仓库中还有不少历史探索脚本和未跟踪目录，本阶段按用户要求不做清理。
- 当前发布链接需要 GitHub Pages 已启用 `docs/` 目录；如果未启用，链接在推送后仍需仓库设置。

## 9. 给下一位 AI 的工作顺序

1. 进入仓库：`D:\GProjects\期末量化分析\quant-research-platform`
2. 检查：`git status --short --branch`
3. 核对发布包：`docs/classroom-report/index.html`
4. 如果用户只要分享链接，先完成 GitHub 认证和 push。
5. 如果用户继续改文，改 `final_narrative_draft.md`，不要直接改发布 HTML。
6. 如果重新渲染 HTML，记得重新插入目录块并同步到 `docs/classroom-report/`。
7. 推送后验证链接：`https://dongcode-af1.github.io/quant-research-platform/classroom-report/`
