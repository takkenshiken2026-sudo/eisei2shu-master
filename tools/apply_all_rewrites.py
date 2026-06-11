#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/rewrites/*.py を slug 名順に guide_articles.csv へ一括適用。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.apply_guide_rewrite_batch import apply_rewrites  # noqa: E402
from tools.rewrite_module_io import discover_rewrite_files, load_rewrites_module  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="全 rewrite 正本を CSV に適用")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--rewrites-dir", type=Path, default=ROOT / "tools" / "rewrites")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    merged: dict[str, dict[str, str]] = {}
    for path in discover_rewrite_files(args.rewrites_dir.resolve()):
        mod = load_rewrites_module(path)
        rewrites = getattr(mod, "REWRITES")
        for slug, patch in rewrites.items():
            if slug in merged:
                print(f"warn: duplicate slug {slug} in {path.name}", file=sys.stderr)
            merged[slug] = patch
    csv_path = root / "data" / "guide_articles.csv"
    n = apply_rewrites(csv_path, merged, dry_run=args.dry_run)
    print(f"apply_all_rewrites: {n} slugs from {len(discover_rewrite_files(args.rewrites_dir.resolve()))} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
