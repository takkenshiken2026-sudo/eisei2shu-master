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

from learning_links_lib import TERM_QUESTION_LINKS_JSON, glossary_match_entries
from question_slug_lib import question_string_id_past

from build_question_pages import (  # noqa: E402
    FIELD_LABEL_JA,
    breadcrumb_label_past,
    compute_widths,
    format_qwidth,
    parse_row,
)


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


def build_links(parsed_rows: list[dict], max_per_term: int = 5) -> dict[str, list[dict]]:
    term_hits: dict[str, list[tuple[tuple, str, str]]] = defaultdict(list)

    for r in parsed_rows:
        blob = f"{r['text']}\n{r['exp']}\n" + "\n".join(r["opts"])
        era_slug = r["era_slug"]
        session = r["session_or_pool"]
        field = r["field"]
        qwidth = r["qwidth"]
        qid = question_string_id_past(era_slug, session, field, qwidth)
        label = (
            f"{breadcrumb_label_past(r['era_raw'], r['month_raw'])}・"
            f"{FIELD_LABEL_JA[field]} 第{r['num']}問"
        )
        sort_key = (era_slug, session, field, r["num"])
        for _name, slug in glossary_match_entries(blob, max_terms=8):
            term_hits[slug].append((sort_key, qid, label))

    out: dict[str, list[dict]] = {}
    for slug, hits in term_hits.items():
        hits.sort(key=lambda x: x[0], reverse=True)
        seen_qid: set[str] = set()
        items: list[dict] = []
        for _sk, qid, label in hits:
            if qid in seen_qid:
                continue
            seen_qid.add(qid)
            items.append({"id": qid, "label": label})
            if len(items) >= max_per_term:
                break
        if items:
            out[slug] = items
    return out


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    rows = load_past_rows(repo)
    if not rows:
        print("過去問 CSV が無いため term-question-links.json は更新しません。")
        return

    links = build_links(rows)
    TERM_QUESTION_LINKS_JSON.write_text(
        json.dumps(links, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"生成: {TERM_QUESTION_LINKS_JSON}（{len(links)} 用語）")


if __name__ == "__main__":
    main()
