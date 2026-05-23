#!/usr/bin/env python3
"""手作りデータで全用語の MD / CSV を一括リライトする。"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HANDMADE = REPO / "tools" / "handmade"

_spec = importlib.util.spec_from_file_location(
    "legacy", REPO / "tools" / "enrich_glossary_priority_legacy.py"
)
_legacy = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_legacy)

patch_md = _legacy.patch_md
sections_with_tips = _legacy.sections_with_tips
exam_points_csv = _legacy.exam_points_csv
common_mistakes_text = _legacy.common_mistakes_text
GLOSSARY_CSV = _legacy.GLOSSARY_CSV


def ensure_table_sections(item: dict) -> dict:
    """tables 未指定の I() エントリに、試験向けの表を自動補完する。"""
    sections = list(item.get("sections") or [])
    table_count = sum(
        1
        for _title, body in sections
        if body and isinstance(body[0], list) and isinstance(body[0][0], str)
    )
    if table_count >= 2:
        return item
    term = item["term"]
    category = item["category"]
    desc = (item.get("csv_desc") or "")[:100]
    tips: list[str] = []
    for title, body in sections:
        if title == "試験で狙われる頻出ポイント" and isinstance(body, list):
            tips = [str(x) for x in body]
    new_sections: list = [
        (
            "要点整理",
            [
                ["観点", "内容"],
                ["用語", term],
                ["分野", category],
                ["要点", desc or f"{term}の定義と試験頻出ポイント"],
            ],
        ),
    ]
    if tips:
        rows = [["よくある誤り", "正しい整理"]]
        for tip in tips[:3]:
            if "→" in tip:
                left, right = tip.split("→", 1)
                rows.append([left.strip("「」 "), right.strip()])
            else:
                rows.append([tip, "条文・数値で確認"])
        new_sections.append(("比較・注意（頻出）", rows))
    new_sections.extend(sections)
    item = dict(item)
    item["sections"] = new_sections
    return item


def update_csv_row_handmade(
    term: str, slug: str, tips: list[str], csv_desc: str
) -> bool:
    import csv

    detail = csv_desc
    if tips:
        detail = f"{csv_desc} 試験では、{tips[0].split('→')[0].strip('「」 ')}などの誤り肢に注意。"
    short = csv_desc if len(csv_desc) <= 120 else csv_desc[:117] + "…"
    with GLOSSARY_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    hit = False
    for row in rows:
        if row.get("term") != term and row.get("slug") != slug:
            continue
        hit = True
        ep = exam_points_csv(tips)
        cm = common_mistakes_text(tips)
        if ep:
            row["exam_points"] = ep
        if cm:
            row["common_mistakes"] = cm
        row["short_def"] = short
        row["definition"] = csv_desc
        row["explanation"] = detail
        row["term_detail_body"] = detail
        break
    if not hit:
        return False
    with GLOSSARY_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return True


def load_handmade_modules() -> list:
    modules = []
    seen_lists: set[int] = set()
    for path in sorted(HANDMADE.glob("glossary_*_data.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(mod)
        for attr in dir(mod):
            if not attr.startswith("HANDMADE"):
                continue
            val = getattr(mod, attr)
            if not isinstance(val, list) or not val or not isinstance(val[0], dict):
                continue
            lid = id(val)
            if lid in seen_lists:
                continue
            seen_lists.add(lid)
            modules.extend(val)
    return modules


def main() -> int:
    items = load_handmade_modules()
    if not items:
        print("手作りデータがありません。tools/handmade/glossary_*_data.py を配置してください。")
        return 1
    by_slug = {item["slug"]: item for item in items}
    duplicates = len(items) - len(by_slug)
    if duplicates:
        print(f"警告: スラッグ重複 {duplicates} 件（後勝ちで上書き）")
    items = list(by_slug.values())
    md_ok = csv_ok = 0
    for item in items:
        item = ensure_table_sections(item)
        sections, tips = sections_with_tips(item)
        if patch_md(item, sections):
            md_ok += 1
        if update_csv_row_handmade(item["term"], item["slug"], tips, item["csv_desc"]):
            csv_ok += 1
    print(f"handmade-rewrite: md={md_ok} csv={csv_ok} / {len(items)} entries")
    if md_ok < 260:
        print("警告: 267語未満です。欠落スラッグを確認してください。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
