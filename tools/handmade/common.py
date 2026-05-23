"""手作り用語リライト共通（import 専用）。"""
from __future__ import annotations


def I(
    term: str,
    slug: str,
    category: str,
    title: str,
    csv_desc: str,
    tips: list[str],
    tables: list | None = None,
) -> dict:
    sections: list = []
    if tables:
        sections.extend(tables)
    sections.append(("試験で狙われる頻出ポイント", tips))
    return {
        "term": term,
        "slug": slug,
        "category": category,
        "title": title,
        "csv_desc": csv_desc,
        "sections": sections,
    }
