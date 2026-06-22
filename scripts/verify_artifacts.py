from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    failures = []
    for manifest_path in (ROOT / "artifacts" / "promoted").glob("**/promotion.json"):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for name, expected in manifest["files"].items():
            actual = hashlib.sha256((manifest_path.parent / name).read_bytes()).hexdigest()
            if actual != expected:
                failures.append(f"{manifest_path.parent / name}: hash mismatch")
    if failures:
        raise SystemExit("\n".join(failures))
    print("promoted artifacts verified")


if __name__ == "__main__":
    main()
