#!/usr/bin/env python3
"""全用語の CSV / MD を読みやすい文体・具体例・覚え方・FAQ4件に更新する。"""
from __future__ import annotations

import csv
import importlib.util
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GLOSSARY_CSV = REPO / "data" / "glossary_terms.csv"
ARTICLES = REPO / "eisei-articles" / "articles"

_spec = importlib.util.spec_from_file_location(
    "rfl", REPO / "tools" / "reader_friendly_lib.py"
)
_rfl = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_rfl)

_spec_legacy = importlib.util.spec_from_file_location(
    "legacy", REPO / "tools" / "enrich_glossary_priority_legacy.py"
)
_legacy = importlib.util.module_from_spec(_spec_legacy)
assert _spec_legacy.loader
_spec_legacy.loader.exec_module(_legacy)
find_md_by_slug = _legacy.find_md_by_slug


def split_semicolon(value: str) -> list[str]:
    return [x.strip() for x in re.split(r"[;；]", value or "") if x.strip()]


def sync_md_frontmatter(slug: str, faqs: list[tuple[str, str]]) -> bool:
    path = find_md_by_slug(slug)
    if not path:
        return False
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False
    fm = parts[1]
    for idx, (q, a) in enumerate(faqs[:4], start=1):
        for key, val in (("question", q), ("answer", a)):
            field = f"faq_{idx}_{key}"
            line = f"{field}: {val}"
            if re.search(rf"^{field}:\s*", fm, re.MULTILINE):
                fm = re.sub(rf"^{field}.*$", line, fm, count=1, flags=re.MULTILINE)
            else:
                fm = fm.rstrip() + f"\n{line}\n"
    path.write_text("---" + fm + "---" + parts[2], encoding="utf-8")
    return True


def ensure_csv_columns(fieldnames: list[str]) -> list[str]:
    extra = [
        "summary_example",
        "faq_3_question",
        "faq_3_answer",
        "faq_4_question",
        "faq_4_answer",
    ]
    out = list(fieldnames)
    for col in extra:
        if col not in out:
            out.append(col)
    return out


def main() -> int:
    with GLOSSARY_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = ensure_csv_columns(reader.fieldnames or [])
        rows = list(reader)

    md_ok = 0
    for row in rows:
        term = (row.get("term") or "").strip()
        slug = (row.get("slug") or "").strip()
        category = (row.get("category") or "労働衛生").strip()
        if not term or not slug:
            continue

        base = row.get("term_detail_body") or row.get("explanation") or row.get("definition") or ""
        tips = _rfl.exam_tips_list(
            row.get("exam_points", ""),
            row.get("common_mistakes", ""),
        )
        related = split_semicolon(row.get("related_terms", ""))

        short = _rfl.plain_short_def(term, category, base)
        summary_ex = _rfl.concrete_example(term, slug, category, tips, related)
        detail = _rfl.plain_definition(term, category, base, tips)
        memory = _rfl.memory_tip_detailed(term, category, tips, related)
        lead = _rfl.plain_article_lead(term, category, short)
        faqs = _rfl.build_faqs(term, category, short, tips, related)

        row["short_def"] = short
        row["definition"] = detail[:200] + ("…" if len(detail) > 200 else "")
        row["explanation"] = detail
        row["term_detail_body"] = detail
        row["article_lead"] = lead
        row["summary_example"] = summary_ex
        row["memory_tip"] = memory
        if tips:
            row["exam_points"] = "；".join(tips[:3])
        mistakes = []
        for t in tips:
            w, r = _rfl.parse_tip_pair(t)
            if w and r:
                mistakes.append(f"誤：{w} → 正：{r}")
        if mistakes:
            row["common_mistakes"] = "；".join(mistakes[:3])

        for idx, (q, a) in enumerate(faqs[:4], start=1):
            row[f"faq_{idx}_question"] = q
            row[f"faq_{idx}_answer"] = a

        if sync_md_frontmatter(slug, faqs):
            md_ok += 1

    with GLOSSARY_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"reader-friendly: csv={len(rows)} md_faq_sync={md_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
