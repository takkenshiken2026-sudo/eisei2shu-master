#!/usr/bin/env python3
"""試験ガイドの定型リード・FAQを修復し、HTMLを再生成する。

`enrich_guide_row` 等で混入した「〜について、第二種衛生管理者試験を目指す方の視点で…」
のような無意味な定型文を除去し、meta_description または git 履歴の元リードに戻す。
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.pro_content.guide_writer import (  # noqa: E402
    dedupe_guide_lead,
    is_boilerplate_lead,
    is_generic_faq,
    lead_from_row,
    professional_faqs,
    split_semicolon,
    topic_from_title,
)

GUIDE_CSV = ROOT / "data" / "guide_articles.csv"
GIT_RESTORE_REF = "70cd5c2:data/guide_articles.csv"
AFFILIATE_TAG = "アフィリエイト"


def load_git_leads(ref: str) -> dict[str, str]:
    try:
        raw = subprocess.check_output(["git", "show", ref], text=True, cwd=ROOT)
    except subprocess.CalledProcessError:
        return {}
    return {
        (row.get("slug") or "").strip(): (row.get("lead") or "").strip()
        for row in csv.DictReader(raw.splitlines())
        if (row.get("slug") or "").strip()
    }


def write_csv_atomic(rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    tmp = GUIDE_CSV.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    if len(list(csv.DictReader(tmp.open(encoding="utf-8")))) != len(rows):
        tmp.unlink(missing_ok=True)
        raise RuntimeError("CSV row count mismatch after write")
    shutil.move(str(tmp), str(GUIDE_CSV))


def repair_row(row: dict[str, str], git_leads: dict[str, str]) -> dict[str, str]:
    tags = split_semicolon(row.get("tags") or "")
    if AFFILIATE_TAG in tags:
        return {"lead": False, "faq": False}

    slug = (row.get("slug") or "").strip()
    changed_lead = False
    changed_faq = False

    old_lead = row.get("lead", "")
    if is_boilerplate_lead(old_lead) or not (old_lead or "").strip():
        candidate = git_leads.get(slug, "")
        if candidate and not is_boilerplate_lead(candidate):
            row["lead"] = dedupe_guide_lead(candidate)
        else:
            row["lead"] = lead_from_row(row)
        changed_lead = row["lead"] != old_lead
    else:
        cleaned = lead_from_row(row)
        if cleaned != old_lead:
            row["lead"] = cleaned
            changed_lead = True

    if is_generic_faq(row):
        faqs = professional_faqs(
            (row.get("title") or "").strip(),
            (row.get("genre") or "試験対策").strip(),
            row.get("lead") or "",
        )
        for n, (q, a) in enumerate(faqs, start=1):
            row[f"faq_{n}_question"] = q
            row[f"faq_{n}_answer"] = a
        changed_faq = True

    return {"lead": changed_lead, "faq": changed_faq}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-build", action="store_true", help="CSVのみ更新しHTMLは再生成しない")
    parser.add_argument("--git-ref", default=GIT_RESTORE_REF, help="リード復元用の git 参照")
    args = parser.parse_args()

    if not GUIDE_CSV.is_file():
        print(f"missing {GUIDE_CSV}", file=sys.stderr)
        return 1

    with GUIDE_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())

    git_leads = load_git_leads(args.git_ref)
    stats = {"lead": 0, "faq": 0, "skipped_affiliate": 0}

    for row in rows:
        if AFFILIATE_TAG in split_semicolon(row.get("tags") or ""):
            stats["skipped_affiliate"] += 1
            continue
        result = repair_row(row, git_leads)
        if result["lead"]:
            stats["lead"] += 1
        if result["faq"]:
            stats["faq"] += 1

    write_csv_atomic(rows, fieldnames)
    print(
        f"fixed leads: {stats['lead']}, faqs: {stats['faq']}, "
        f"affiliate skipped: {stats['skipped_affiliate']}, total: {len(rows)}"
    )

    remaining = sum(
        1
        for r in rows
        if AFFILIATE_TAG not in split_semicolon(r.get("tags") or "")
        and is_boilerplate_lead(r.get("lead", ""))
    )
    if remaining:
        print(f"WARNING: {remaining} articles still have boilerplate leads", file=sys.stderr)
        return 1

    if not args.no_build:
        import tools.build_article_pages as build  # noqa: WPS433

        build.main()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
