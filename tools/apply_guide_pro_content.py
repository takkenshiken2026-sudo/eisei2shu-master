#!/usr/bin/env python3
"""試験ガイド全件をプロ品質に更新（guide_articles.csv）。"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GUIDE_CSV = REPO / "data" / "guide_articles.csv"

sys.path.insert(0, str(REPO / "tools"))
from guide_pro_content_lib import patch_row  # noqa: E402


def ensure_columns(fieldnames: list[str]) -> list[str]:
    extra = ["faq_3_question", "faq_3_answer", "faq_4_question", "faq_4_answer"]
    out = list(fieldnames or [])
    for c in extra:
        if c not in out:
            out.append(c)
    return out


def main() -> int:
    with GUIDE_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = ensure_columns(reader.fieldnames)
        rows = list(reader)

    updated = 0
    for row in rows:
        if (row.get("content_status") or "").strip() != "published":
            continue
        patch_row(row)
        updated += 1

    with GUIDE_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"guide-pro: published={updated} total_rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
