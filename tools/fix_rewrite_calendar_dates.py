#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rewrite 正本の載せ過ぎ具体日を整理（guide_date_prose ルール適用）。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.guide_date_prose import audit_date_density, soften_dates_for_column  # noqa: E402
from tools.rewrite_module_io import discover_rewrite_files, load_rewrites_module, write_rewrite_module  # noqa: E402

TEXT_COLS = (
    "lead",
    "user_intent",
    "meta_description",
    "action_items",
    "key_points",
)


def trim_file(path: Path) -> tuple[bool, list[str]]:
    mod = load_rewrites_module(path)
    rewrites = getattr(mod, "REWRITES")
    slug = next(iter(rewrites))
    patch = dict(rewrites[slug])
    changed = False
    for col in TEXT_COLS:
        val = patch.get(col)
        if not isinstance(val, str) or not val.strip():
            continue
        fixed = soften_dates_for_column(val, slug=slug, col=col)
        if fixed != val:
            patch[col] = fixed
            changed = True
    warnings = audit_date_density(slug, patch)
    if changed:
        write_rewrite_module(path, slug, {slug: patch})
    return changed, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="rewrite 具体日の載せ過ぎ整理")
    ap.add_argument("--rewrites-dir", type=Path, default=ROOT / "tools" / "rewrites")
    ap.add_argument("--audit-only", action="store_true")
    args = ap.parse_args()
    changed = 0
    all_warnings: list[str] = []
    for path in discover_rewrite_files(args.rewrites_dir.resolve()):
        if args.audit_only:
            mod = load_rewrites_module(path)
            slug = next(iter(getattr(mod, "REWRITES")))
            all_warnings.extend(audit_date_density(slug, getattr(mod, "REWRITES")[slug]))
            continue
        ok, warnings = trim_file(path)
        if ok:
            changed += 1
        all_warnings.extend(warnings)
    if args.audit_only:
        print(f"audit: {len(all_warnings)} over-limit columns")
    else:
        print(f"trim_rewrite_calendar_dates: {changed} files changed")
    for w in all_warnings[:30]:
        print(f"  warn: {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
