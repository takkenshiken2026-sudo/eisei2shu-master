#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""予想模試3回分・無料サンプル3問を past_questions.csv 形式で出力する。"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_MOCK = DATA / "mock_exam_questions.csv"
OUT_SAMPLE = DATA / "free_sample_questions.csv"
OUT_INDEX = DATA / "mock_exam_sets.json"
BANK = Path(__file__).resolve().parent / "mock_exam_question_bank.json"

HEADER = [
    "exam_year",
    "exam_wareki",
    "question_no",
    "type",
    "category",
    "tags",
    "stem",
    "preamble",
    "statement_a",
    "statement_b",
    "statement_c",
    "statement_d",
    "choice_1",
    "choice_2",
    "choice_3",
    "choice_4",
    "choice_5",
    "correct",
    "is_exempt",
    "is_invalidated",
    "note",
    "explanation",
    "explanation_summary",
    "explanation_correct",
    "explanation_choices",
    "explanation_point",
    "related_links",
]


def row(
    exam_year: int,
    exam_wareki: str,
    question_no: int,
    category: str,
    stem: str,
    choices: list[str],
    correct: int,
    explanation: str,
    tags: str = "予想模試",
) -> dict[str, str]:
    if len(choices) != 5:
        raise ValueError(f"need 5 choices: {stem[:40]}")
    return {
        "exam_year": str(exam_year),
        "exam_wareki": exam_wareki,
        "question_no": str(question_no),
        "type": "single",
        "category": category,
        "tags": tags,
        "stem": stem,
        "preamble": "",
        "statement_a": "",
        "statement_b": "",
        "statement_c": "",
        "statement_d": "",
        "choice_1": choices[0],
        "choice_2": choices[1],
        "choice_3": choices[2],
        "choice_4": choices[3],
        "choice_5": choices[4],
        "correct": str(correct),
        "is_exempt": "FALSE",
        "is_invalidated": "FALSE",
        "note": "",
        "explanation": explanation,
        "explanation_summary": "",
        "explanation_correct": "",
        "explanation_choices": "",
        "explanation_point": "",
        "related_links": "",
    }


def load_bank() -> dict:
    with BANK.open(encoding="utf-8") as f:
        return json.load(f)


def build_set_rows(set_id: int, title: str, questions: list[dict]) -> list[dict]:
    exam_year = 9000 + set_id
    rows = []
    for i, q in enumerate(questions, start=1):
        rows.append(
            row(
                exam_year,
                title,
                i,
                q["category"],
                q["stem"],
                q["choices"],
                q["correct"],
                q["explanation"],
                q.get("tags", "予想模試"),
            )
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    bank = load_bank()
    mock_rows: list[dict] = []
    sets_meta = []

    for s in bank["mock_sets"]:
        set_id = s["set_id"]
        title = s["title"]
        qs = s["questions"]
        mock_rows.extend(build_set_rows(set_id, title, qs))
        cats = {}
        for q in qs:
            cats[q["category"]] = cats.get(q["category"], 0) + 1
        sets_meta.append(
            {
                "set_id": set_id,
                "exam_year": 9000 + set_id,
                "title": title,
                "question_count": len(qs),
                "category_distribution": cats,
                "csv_file": "mock_exam_questions.csv",
            }
        )

    sample_rows = build_set_rows(0, "無料サンプル", bank["free_samples"])
    for r in sample_rows:
        r["exam_year"] = "8000"
        r["tags"] = "無料サンプル"

    write_csv(OUT_MOCK, mock_rows)
    write_csv(OUT_SAMPLE, sample_rows)

    index = {
        "exam": "第二種衛生管理者試験",
        "format": "past_questions.csv互換（30問×5択・3分野各10問）",
        "mock_sets": sets_meta,
        "free_sample": {
            "exam_year": 8000,
            "title": "無料サンプル",
            "question_count": len(sample_rows),
            "csv_file": "free_sample_questions.csv",
        },
        "source_past_questions": "/Users/otedaiki/Desktop/past_questions.csv",
    }
    OUT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote {OUT_MOCK} ({len(mock_rows)} rows)")
    print(f"wrote {OUT_SAMPLE} ({len(sample_rows)} rows)")
    print(f"wrote {OUT_INDEX}")


if __name__ == "__main__":
    main()
