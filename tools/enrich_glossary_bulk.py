#!/usr/bin/env python3
"""既存用語をバッチ単位で exam_points・本文に充実する。"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "legacy", REPO / "tools" / "enrich_glossary_priority_legacy.py"
)
_legacy = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_legacy)

for name, path in [
    ("b2", "glossary_enrich_batch2_data.py"),
    ("b3", "glossary_enrich_batch3_data.py"),
    ("b5", "glossary_enrich_batch5_data.py"),
]:
    spec = importlib.util.spec_from_file_location(name, REPO / "tools" / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    if name == "b2":
        _b2 = mod
    elif name == "b3":
        _b3 = mod
    else:
        _b5 = mod

patch_md = _legacy.patch_md
update_csv_row = _legacy.update_csv_row
sections_with_tips = _legacy.sections_with_tips


def run_batch(items: list[dict], label: str) -> tuple[int, int]:
    md_ok = csv_ok = 0
    for item in items:
        sections, tips = sections_with_tips(item)
        if patch_md(item, sections):
            md_ok += 1
        if update_csv_row(item["term"], item["slug"], tips, item["csv_desc"]):
            csv_ok += 1
    print(f"{label}: md={md_ok}, csv={csv_ok} / {len(items)}")
    return md_ok, csv_ok


def main() -> None:
    m1, c1 = run_batch(_legacy.PRIORITY, "priority-1")
    m2, c2 = run_batch(_b2.BATCH2, "batch-2")
    m3, c3 = run_batch(_b3.BATCH3, "batch-3")
    m5, c5 = run_batch(_b5.BATCH5, "batch-5")
    print(f"bulk total: md={m1+m2+m3+m5}, csv={c1+c2+c3+c5}")

    _spec_fill = importlib.util.spec_from_file_location(
        "fill", REPO / "tools" / "enrich_glossary_fill_remaining.py"
    )
    _fill = importlib.util.module_from_spec(_spec_fill)
    assert _spec_fill.loader
    _spec_fill.loader.exec_module(_fill)
    _fill.main()


if __name__ == "__main__":
    main()
