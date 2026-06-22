from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote an audited run")
    parser.add_argument("run_id")
    parser.add_argument("experiment_id")
    args = parser.parse_args()
    source = ROOT / "workspace" / "runs" / args.run_id
    if not (source / "result.json").exists():
        raise SystemExit(f"Completed result not found: {args.run_id}")
    target = ROOT / "artifacts" / "promoted" / args.experiment_id / args.run_id
    if target.exists():
        raise SystemExit("Promotion target already exists; promoted runs are immutable")
    shutil.copytree(source, target)
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in target.iterdir()
        if path.is_file()
    }
    (target / "promotion.json").write_text(
        json.dumps(
            {"experiment_id": args.experiment_id, "run_id": args.run_id, "files": hashes}, indent=2
        ),
        encoding="utf-8",
    )
    print(target)


if __name__ == "__main__":
    main()
