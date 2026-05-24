#!/usr/bin/env python3
"""用語267件・試験ガイド100件を専門家×プロライター品質に一括引き上げ。"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.pro_content.glossary_writer import enrich_glossary_row  # noqa: E402
from tools.pro_content.guide_writer import enrich_guide_row  # noqa: E402
from tools.pro_content.load_handmade import load_handmade_by_slug  # noqa: E402

GLOSSARY_CSV = ROOT / "data" / "glossary_terms.csv"
GUIDE_CSV = ROOT / "data" / "guide_articles.csv"
ARTICLES = ROOT / "eisei-articles" / "articles"


def split_semicolon(value: str) -> list[str]:
    return [x.strip() for x in re.split(r"[;；]", value or "") if x.strip()]


def sync_glossary_md_faq(slug: str, row: dict) -> bool:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "legacy", ROOT / "tools" / "enrich_glossary_priority_legacy.py"
    )
    legacy = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(legacy)
    path = legacy.find_md_by_slug(slug)
    if not path:
        return False
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False
    fm = parts[1]
    for idx in range(1, 5):
        q = (row.get(f"faq_{idx}_question") or "").strip()
        a = (row.get(f"faq_{idx}_answer") or "").strip()
        if not q or not a:
            continue
        for key, val in (("question", q), ("answer", a)):
            field = f"faq_{idx}_{key}"
            line = f"{field}: {val}"
            if re.search(rf"^{field}:\s*", fm, re.MULTILINE):
                fm = re.sub(rf"^{field}.*$", line, fm, count=1, flags=re.MULTILINE)
            else:
                fm = fm.rstrip() + f"\n{line}\n"
    path.write_text("---" + fm + "---" + parts[2], encoding="utf-8")
    return True


def ensure_columns(fieldnames: list[str], extra: list[str]) -> list[str]:
    out = list(fieldnames)
    for col in extra:
        if col not in out:
            out.append(col)
    return out


def apply_glossary() -> tuple[int, int]:
    handmade = load_handmade_by_slug()
    with GLOSSARY_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        extra = [
            "summary_example",
            "faq_3_question",
            "faq_3_answer",
            "faq_4_question",
            "faq_4_answer",
        ]
        fieldnames = ensure_columns(reader.fieldnames or [], extra)
        rows = list(reader)
    md_ok = 0
    for row in rows:
        slug = (row.get("slug") or "").strip()
        if not slug:
            continue
        related = split_semicolon(row.get("related_terms", ""))
        enrich_glossary_row(row, handmade.get(slug), related)
        if sync_glossary_md_faq(slug, row):
            md_ok += 1
    with GLOSSARY_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return len(rows), md_ok


def apply_guides() -> int:
    with GUIDE_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        extra = [
            "faq_3_question",
            "faq_3_answer",
            "faq_4_question",
            "faq_4_answer",
        ]
        fieldnames = ensure_columns(reader.fieldnames or [], extra)
        rows = list(reader)
    for row in rows:
        enrich_guide_row(row)
    with GUIDE_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main() -> int:
    g_n, g_md = apply_glossary()
    gu_n = apply_guides()
    print(f"pro-content: glossary={g_n} (md_faq={g_md}), guides={gu_n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
