#!/usr/bin/env python3
"""glossary_terms.csv の related_terms が空の行に、同分野の関連語を付与する。"""
from __future__ import annotations

import csv
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GLOSSARY_CSV = REPO / "data" / "glossary_terms.csv"

# 分野内で優先してつなぐ代表語（試験導線）
PRIORITY_BY_CATEGORY: dict[str, list[str]] = {
    "関係法令": [
        "衛生管理者",
        "産業医",
        "労働安全衛生法",
        "安全衛生委員会",
        "定期健康診断・雇入時健康診断",
        "作業環境測定",
    ],
    "労働衛生": [
        "作業環境測定",
        "局所排気装置",
        "WBGT",
        "許容濃度・管理濃度",
        "捕集分析法",
        "個人用保護具",
    ],
    "労働生理": [
        "熱中症",
        "WBGT",
        "粉じん",
        "騒音",
        "一酸化炭素中毒",
        "感染症",
    ],
}


def main() -> None:
    with GLOSSARY_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    by_cat: dict[str, list[tuple[str, str]]] = {}
    for row in rows:
        cat = (row.get("category") or "").strip()
        term = (row.get("term") or "").strip()
        slug = (row.get("slug") or "").strip()
        if cat and term and slug:
            by_cat.setdefault(cat, []).append((term, slug))

    updated = 0
    for row in rows:
        if (row.get("related_terms") or "").strip():
            continue
        cat = (row.get("category") or "").strip()
        term = (row.get("term") or "").strip()
        if not cat or not term:
            continue
        chosen: list[str] = []
        for p in PRIORITY_BY_CATEGORY.get(cat, []):
            if p != term and p not in chosen:
                chosen.append(p)
            if len(chosen) >= 4:
                break
        for other, _ in by_cat.get(cat, []):
            if other != term and other not in chosen:
                chosen.append(other)
            if len(chosen) >= 5:
                break
        if chosen:
            row["related_terms"] = ";".join(chosen)
            updated += 1

    with GLOSSARY_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"populate related_terms: {updated} rows updated")


if __name__ == "__main__":
    main()
