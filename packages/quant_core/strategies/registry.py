from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import yaml


@dataclass
class RegisteredStrategy:
    metadata: dict
    module: ModuleType
    path: Path


class StrategyRegistry:
    def __init__(self, root: Path):
        self.root = root
        self.items: dict[str, RegisteredStrategy] = {}

    def reload(self) -> list[dict]:
        self.items.clear()
        for manifest in sorted(self.root.glob("**/strategy.yml")):
            metadata = yaml.safe_load(manifest.read_text(encoding="utf-8"))
            source = manifest.with_name("strategy.py")
            spec = importlib.util.spec_from_file_location(f"qrp_strategy_{metadata['id']}", source)
            if not spec or not spec.loader:
                raise ImportError(f"Cannot load strategy {metadata['id']}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if not hasattr(module, "generate_targets"):
                raise TypeError(f"Strategy {metadata['id']} lacks generate_targets")
            self.items[metadata["id"]] = RegisteredStrategy(metadata, module, manifest.parent)
        return self.list()

    def list(self) -> list[dict]:
        return [item.metadata for item in self.items.values()]

    def get(self, strategy_id: str) -> RegisteredStrategy:
        if strategy_id not in self.items:
            raise KeyError(strategy_id)
        return self.items[strategy_id]
