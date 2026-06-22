# 策略开发

新策略位于 `strategies/experimental/E###-name`，包含一个清单、一个实现、一个 README 和聚焦测试。实现唯一入口：

```python
generate_targets(context, parameters) -> dict[str, float]
```

策略不得自行读取网络数据、移动成交日期、计算成本或写结果。通过预注册测试和人工审查后，迁入 `strategies/library`，旧版本不覆盖。

