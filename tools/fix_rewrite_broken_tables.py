#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rewrite 正本の壊れた markdown 表（改行欠落·|| 連結）を修復して再書き込み。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.rewrite_module_io import (  # noqa: E402
    discover_rewrite_files,
    load_rewrites_module,
    repair_markdown_tables,
    write_rewrite_module,
)

BODY_KEYS = tuple(f"section_{n}_body" for n in range(1, 8))


def fix_file(path: Path) -> bool:
    mod = load_rewrites_module(path)
    rewrites = getattr(mod, "REWRITES")
    slug = next(iter(rewrites))
    patch = dict(rewrites[slug])
    changed = False
    for key in BODY_KEYS:
        val = patch.get(key)
        if not isinstance(val, str) or not val:
            continue
        fixed = repair_markdown_tables(val)
        if fixed != val:
            patch[key] = fixed
            changed = True
    if changed:
        write_rewrite_module(path, slug, {slug: patch})
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description="rewrite 正本の表 markdown 修復")
    ap.add_argument("--rewrites-dir", type=Path, default=ROOT / "tools" / "rewrites")
    args = ap.parse_args()
    n = sum(1 for p in discover_rewrite_files(args.rewrites_dir.resolve()) if fix_file(p))
    print(f"fix_rewrite_broken_tables: {n} files repaired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
