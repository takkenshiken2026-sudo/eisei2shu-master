#!/usr/bin/env python3
"""汎用テンプレ・薄い用語を一括で試験向け本文に差し替える。"""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GLOSSARY_CSV = REPO / "data" / "glossary_terms.csv"

_spec_legacy = importlib.util.spec_from_file_location(
    "legacy", REPO / "tools" / "enrich_glossary_priority_legacy.py"
)
_legacy = importlib.util.module_from_spec(_spec_legacy)
assert _spec_legacy.loader
_spec_legacy.loader.exec_module(_legacy)

_spec_fill = importlib.util.spec_from_file_location(
    "fill", REPO / "tools" / "enrich_glossary_fill_remaining.py"
)
_fill = importlib.util.module_from_spec(_spec_fill)
assert _spec_fill.loader
_spec_fill.loader.exec_module(_fill)

_spec_ql = importlib.util.spec_from_file_location(
    "ql", REPO / "tools" / "glossary_quality_lib.py"
)
_ql = importlib.util.module_from_spec(_spec_ql)
assert _spec_ql.loader
_spec_ql.loader.exec_module(_ql)

patch_md = _legacy.patch_md
update_csv_row = _legacy.update_csv_row
sections_with_tips = _legacy.sections_with_tips
tips_for_row = _fill.tips_for_row
EXTRA_TIPS = _fill.EXTRA_TIPS


def should_upgrade(row: dict, md_text: str) -> bool:
    slug = row.get("slug", "")
    if _ql.is_generic_exam_points(row.get("exam_points", "")):
        return True
    if slug in EXTRA_TIPS:
        return True
    if _ql.is_thin_row(row):
        return True
    if _ql.md_needs_upgrade(md_text) and not _ql.md_quality_ok(md_text):
        return True
    return False


def main() -> None:
    rows = list(csv.DictReader(GLOSSARY_CSV.open(encoding="utf-8")))
    md_ok = csv_ok = skipped = 0
    for row in rows:
        slug = row.get("slug", "")
        md_path = _legacy.find_md_by_slug(slug)
        md_text = md_path.read_text(encoding="utf-8") if md_path else ""
        if not should_upgrade(row, md_text):
            skipped += 1
            continue
        tips = tips_for_row(row)
        term = row["term"]
        category = row.get("category", "労働衛生")
        raw_title = (row.get("title") or f"{term}とは？").split("【")[0].strip()
        if "とは" not in raw_title:
            raw_title = f"{term}とは？試験頻出の整理"
        short_def = (row.get("short_def") or row.get("definition") or "").strip()
        csv_desc = _ql.expand_explanation(term, category, short_def, tips)
        sections = _ql.auto_sections(term, category, short_def, tips)
        item = {
            "term": term,
            "slug": slug,
            "category": category,
            "title": raw_title,
            "csv_desc": csv_desc,
            "sections": sections,
        }
        merged_sections, merged_tips = sections_with_tips(item)
        if patch_md(item, merged_sections):
            md_ok += 1
        if update_csv_row(term, slug, merged_tips, csv_desc):
            csv_ok += 1
    print(
        f"quality-finish: upgraded md={md_ok} csv={csv_ok} "
        f"skipped={skipped} total={len(rows)}"
    )


if __name__ == "__main__":
    main()
