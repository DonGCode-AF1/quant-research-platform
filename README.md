# Quant Research Platform

一个面向课程研究的可追溯量化平台：策略插件、统一回测、实验登记、结果提升和课堂展示彼此解耦。

## 快速开始

```powershell
uv sync --all-extras
npm.cmd install
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/dev.ps1
```

打开 `http://127.0.0.1:5173`。示例数据是确定性合成快照，仅用于验收数据获取到回测结果的完整链路。

课堂展示可独立构建：`quarto render projects/classroom-presentation --to revealjs`。

## 研究工作流

1. 在 `strategies/experimental/E###-*` 创建策略插件。
2. 在 `experiments/registry.yml` 预注册问题、唯一变化与指标。
3. 从 UI 或 API 运行回测；临时结果进入 `workspace/runs`。
4. 审查代码提交、数据哈希、交易约束和结果后，使用 `scripts/promote_run.py` 提升。
5. 课堂展示只读取 `artifacts/promoted`，不直接引用临时运行。

详细规则见 [docs/index.md](docs/index.md)。
