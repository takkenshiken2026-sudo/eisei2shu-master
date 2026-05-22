#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
過去問 CSV から用語スラッグ ↔ 問題 ID の対応表 docs/term-question-links.json を生成する。

使用例:
  python3 tools/build_term_question_links.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from learning_links_lib import (
    TERM_QUESTION_LINKS_JSON,
    glossary_match_entries,
    load_glossary_slugs,
    question_id_to_web_path,
)
from question_slug_lib import question_string_id_past

from build_question_pages import (  # noqa: E402
    FIELD_LABEL_JA,
    breadcrumb_label_past,
    compute_widths,
    format_qwidth,
    parse_row,
)


def past_page_exists(repo_root: Path, qid: str) -> bool:
    web = question_id_to_web_path(qid)
    if not web:
        return False
    rel = web.strip("/") + "/index.html"
    return (repo_root / rel).is_file()


def load_past_rows(repo_root: Path) -> list[dict]:
    path = repo_root / "data" / "eisei2_past_questions.csv"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8-sig")
    rows = []
    for i, row in enumerate(csv.DictReader(text.splitlines()), start=2):
        try:
            parsed = parse_row(row, i)
        except Exception:
            continue
        if parsed["is_orig"]:
            continue
        rows.append(parsed)
    if not rows:
        return rows
    widths = compute_widths(rows)
    for r in rows:
        r["qwidth"] = format_qwidth(r["num"], widths[r["group_key"]])
    return rows


def load_related_slug_map(repo_root: Path) -> dict[str, list[str]]:
    """用語スラッグ → 関連用語スラッグ（glossary_terms.csv の related_terms）。"""
    name_to_slug = load_glossary_slugs()
    path = repo_root / "data" / "glossary_terms.csv"
    out: dict[str, list[str]] = {}
    if not path.is_file():
        return out
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            slug = (row.get("slug") or "").strip()
            if not slug:
                continue
            related: list[str] = []
            for part in (row.get("related_terms") or "").split(";"):
                part = part.strip()
                if not part:
                    continue
                rs = name_to_slug.get(part)
                if rs and rs != slug and rs not in related:
                    related.append(rs)
            if related:
                out[slug] = related[:6]
    return out


def build_links(
    parsed_rows: list[dict],
    repo_root: Path,
    max_per_term: int = 8,
    related_map: dict[str, list[str]] | None = None,
) -> dict[str, list[dict]]:
    term_hits: dict[str, list[tuple[tuple, str, str, int]]] = defaultdict(list)
    related_map = related_map or {}

    for r in parsed_rows:
        blob = f"{r['text']}\n{r['exp']}\n" + "\n".join(r["opts"])
        era_slug = r["era_slug"]
        session = r["session_or_pool"]
        field = r["field"]
        qwidth = r["qwidth"]
        qid = question_string_id_past(era_slug, session, field, qwidth)
        if not past_page_exists(repo_root, qid):
            continue
        label = (
            f"{breadcrumb_label_past(r['era_raw'], r['month_raw'])}・"
            f"{FIELD_LABEL_JA[field]} 第{r['num']}問"
        )
        sort_key = (era_slug, session, field, r["num"])
        primary = glossary_match_entries(blob, max_terms=12)
        primary_slugs = {slug for _, slug in primary}
        for _name, slug in primary:
            term_hits[slug].append((sort_key, qid, label, 1))

        supplemental: set[str] = set()
        for _name, slug in primary:
            for rel_slug in related_map.get(slug, []):
                if rel_slug in primary_slugs or rel_slug in supplemental:
                    continue
                supplemental.add(rel_slug)
                term_hits[rel_slug].append((sort_key, qid, label, 0))
                if len(supplemental) >= 6:
                    break
            if len(supplemental) >= 6:
                break

    out: dict[str, list[dict]] = {}
    for slug, hits in term_hits.items():
        hits.sort(key=lambda x: (x[0], x[3]), reverse=True)
        seen_qid: set[str] = set()
        items: list[dict] = []
        for _sk, qid, label, _pri in hits:
            if qid in seen_qid:
                continue
            seen_qid.add(qid)
            items.append({"id": qid, "label": label})
            if len(items) >= max_per_term:
                break
        if items:
            out[slug] = items
    return out


CATEGORY_TO_FIELD = {
    "関係法令": "law",
    "労働衛生": "rights",
    "労働生理": "limit",
}


def load_slug_categories(repo_root: Path) -> dict[str, str]:
    path = repo_root / "data" / "glossary_terms.csv"
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            slug = (row.get("slug") or "").strip()
            cat = (row.get("category") or "").strip()
            if slug and cat:
                out[slug] = cat
    return out


def apply_field_fallback(
    links: dict[str, list[dict]],
    parsed_rows: list[dict],
    repo_root: Path,
    all_slugs: set[str],
    slug_categories: dict[str, str],
    per_term: int = 3,
) -> int:
    """本文マッチが無い用語に、同一科目の直近過去問を付与（学習導線の最低限）。"""
    by_field: dict[str, list[tuple[tuple, str, str]]] = defaultdict(list)
    for r in parsed_rows:
        qid = question_string_id_past(
            r["era_slug"], r["session_or_pool"], r["field"], r["qwidth"]
        )
        if not past_page_exists(repo_root, qid):
            continue
        label = (
            f"{breadcrumb_label_past(r['era_raw'], r['month_raw'])}・"
            f"{FIELD_LABEL_JA[r['field']]} 第{r['num']}問"
        )
        sort_key = (r["era_slug"], r["session_or_pool"], r["field"], r["num"])
        by_field[r["field"]].append((sort_key, qid, label))
    for field in by_field:
        by_field[field].sort(key=lambda x: x[0], reverse=True)

    added = 0
    for slug in sorted(all_slugs):
        if links.get(slug):
            continue
        cat = slug_categories.get(slug, "関係法令")
        field = CATEGORY_TO_FIELD.get(cat, "law")
        pool = by_field.get(field, [])
        seen: set[str] = set()
        items: list[dict] = []
        for _sk, qid, label in pool:
            if qid in seen:
                continue
            seen.add(qid)
            items.append({"id": qid, "label": label})
            if len(items) >= per_term:
                break
        if items:
            links[slug] = items
            added += 1
    return added


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    rows = load_past_rows(repo)
    if not rows:
        print("過去問 CSV が無いため term-question-links.json は更新しません。")
        return

    related_map = load_related_slug_map(repo)
    links = build_links(rows, repo, related_map=related_map)
    slug_categories = load_slug_categories(repo)
    all_slugs = set(slug_categories)
    direct = len(links)
    fallback = apply_field_fallback(links, rows, repo, all_slugs, slug_categories)
    TERM_QUESTION_LINKS_JSON.write_text(
        json.dumps(links, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"生成: {TERM_QUESTION_LINKS_JSON}（{len(links)} 用語・"
        f"本文マッチ {direct}・科目フォールバック {fallback}）"
    )


if __name__ == "__main__":
    main()
