#!/usr/bin/env python3
"""全267用語を専門家・プロライター水準の文案に更新（CSV + MD FAQ）。"""
from __future__ import annotations

import csv
import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GLOSSARY_CSV = REPO / "data" / "glossary_terms.csv"

_spec = importlib.util.spec_from_file_location("pro", REPO / "tools" / "pro_content_lib.py")
_pro = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_pro)

_spec_legacy = importlib.util.spec_from_file_location(
    "legacy", REPO / "tools" / "enrich_glossary_priority_legacy.py"
)
_legacy = importlib.util.module_from_spec(_spec_legacy)
assert _spec_legacy.loader
_spec_legacy.loader.exec_module(_legacy)
find_md_by_slug = _legacy.find_md_by_slug

HANDMADE_TIPS = _pro.load_handmade_tips_by_slug()


def split_semicolon(value: str) -> list[str]:
    return [x.strip() for x in re.split(r"[;；]", value or "") if x.strip()]


def sync_md_faq(slug: str, faqs: list[tuple[str, str]]) -> bool:
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


def ensure_columns(fieldnames: list[str]) -> list[str]:
    extra = ["summary_example", "faq_3_question", "faq_3_answer", "faq_4_question", "faq_4_answer"]
    out = list(fieldnames or [])
    for c in extra:
        if c not in out:
            out.append(c)
    return out


def main() -> int:
    with GLOSSARY_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = ensure_columns(reader.fieldnames)
        rows = list(reader)

    md_ok = 0
    for row in rows:
        term = (row.get("term") or "").strip()
        slug = (row.get("slug") or "").strip()
        category = (row.get("category") or "労働衛生").strip()
        if not term or not slug:
            continue

        core = (
            row.get("term_detail_body")
            or row.get("explanation")
            or row.get("definition")
            or row.get("short_def")
            or ""
        )
        tips = _pro.tips_from_row(row, HANDMADE_TIPS)
        related = split_semicolon(row.get("related_terms", ""))

        short = _pro.expert_short_def(term, category, core)
        summary_ex = _pro.expert_summary_example(term, slug, category, tips, related)
        detail = _pro.expert_detail_body(term, category, core, tips, related)
        memory = _pro.expert_memory_tip(term, category, tips, related)
        lead = _pro.expert_article_lead(term, category)
        faqs = _pro.expert_faqs(term, category, short, detail, tips, related)

        row["short_def"] = short
        row["definition"] = detail[:220] + ("…" if len(detail) > 220 else "")
        row["explanation"] = detail
        row["term_detail_body"] = detail
        row["article_lead"] = lead
        row["summary_example"] = summary_ex
        row["memory_tip"] = memory
        row["exam_points"] = _pro.expert_exam_points(tips)
        row["common_mistakes"] = _pro.expert_common_mistakes(tips)

        for idx, (q, a) in enumerate(faqs, start=1):
            row[f"faq_{idx}_question"] = q
            row[f"faq_{idx}_answer"] = a

        if sync_md_faq(slug, faqs):
            md_ok += 1

    with GLOSSARY_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"glossary-pro: terms={len(rows)} md_faq={md_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
