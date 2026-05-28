#!/usr/bin/env python3
"""用語データの品質サマリを出力。"""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GLOSSARY_CSV = REPO / "data" / "glossary_terms.csv"

_spec = importlib.util.spec_from_file_location(
    "ql", REPO / "tools" / "glossary_quality_lib.py"
)
_ql = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_ql)

_spec_legacy = importlib.util.spec_from_file_location(
    "legacy", REPO / "tools" / "enrich_glossary_priority_legacy.py"
)
_legacy = importlib.util.module_from_spec(_spec_legacy)
assert _spec_legacy.loader
_spec_legacy.loader.exec_module(_legacy)
find_md_by_slug = _legacy.find_md_by_slug


def find_md(slug: str) -> str:
    path = find_md_by_slug(slug)
    return path.read_text(encoding="utf-8") if path else ""


def main() -> None:
    rows = list(csv.DictReader(GLOSSARY_CSV.open(encoding="utf-8")))
    generic = thin = weak_md = ok = 0
    for row in rows:
        slug = row.get("slug", "")
        ep = row.get("exam_points", "")
        if _ql.is_generic_exam_points(ep):
            generic += 1
        if _ql.is_thin_row(row):
            thin += 1
        md = find_md(slug)
        if _ql.md_quality_ok(md):
            ok += 1
        elif _ql.md_needs_upgrade(md):
            weak_md += 1
    print(f"用語数: {len(rows)}")
    print(f"汎用 exam_points: {generic}")
    print(f"薄い CSV 本文: {thin}")
    print(f"MD 要改善: {weak_md}")
    print(f"MD 充実済み: {ok}")


if __name__ == "__main__":
    main()
