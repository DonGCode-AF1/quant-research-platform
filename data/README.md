# 数据治理

Git 只保存体积受控、许可明确的冻结快照及其清单。每个清单记录来源、覆盖期、字段、生成脚本和 SHA256。`demo-cn-etf-synthetic-v1` 是合成验收数据，不可用于投资结论。

真实数据接入应新增 provider 和快照清单；AKShare 等抓取缓存放入 `workspace/cache`，经许可与完整性审查后才冻结。

