#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data/eisei2_original_questions.csv（210問・5択）→ data/practice_questions.csv

二衛マスター専用。静的 q/practice/ 用 CSV を生成する。

  python3 tools/import_eisei2_original_to_practice_csv.py
  python3 tools/import_eisei2_original_to_practice_csv.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.site_config import field_labels  # noqa: E402

SOURCE = ROOT / "data" / "eisei2_original_questions.csv"
OUTPUT = ROOT / "data" / "practice_questions.csv"

SUBJECT_TO_CATEGORY = {
    "関係法令": "関係法令",
    "労働衛生": "労働衛生",
    "労働生理": "労働生理",
}

CSV_COLUMNS = [
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
    "explanation",
    "explanation_summary",
    "explanation_correct",
    "explanation_choices",
    "explanation_point",
]


def norm(s: str | None) -> str:
    return (s or "").strip()


def category_for_subject(subject: str) -> str:
    subj = norm(subject)
    if subj in SUBJECT_TO_CATEGORY:
        return SUBJECT_TO_CATEGORY[subj]
    if subj in field_labels().values():
        return subj
    raise ValueError(f"未対応の科目: {subject!r}")


def row_to_practice(qno: int, row: dict, line_no: int) -> dict[str, str]:
    stem = norm(row.get("問"))
    if not stem:
        raise ValueError(f"行 {line_no}: 問（stem）が空")
    opts = [norm(row.get(f"({i})")) for i in range(1, 6)]
    if not all(opts):
        raise ValueError(f"行 {line_no}: 選択肢 (1)〜(5) が欠けています")
    raw_ans = norm(row.get("正答番号"))
    if not raw_ans.isdigit() or not (1 <= int(raw_ans) <= 5):
        raise ValueError(f"行 {line_no}: 正答番号が不正: {raw_ans!r}")
    ans = int(raw_ans)
    exp = norm(row.get("解説")) or "（解説は未入力です。）"
    subject = norm(row.get("科目"))
    category = category_for_subject(subject)
    return {
        "question_no": str(qno),
        "type": "single",
        "category": category,
        "tags": f"演習;{subject}",
        "stem": stem,
        "preamble": "",
        "statement_a": "",
        "statement_b": "",
        "statement_c": "",
        "statement_d": "",
        "choice_1": opts[0],
        "choice_2": opts[1],
        "choice_3": opts[2],
        "choice_4": opts[3],
        "choice_5": opts[4],
        "correct": str(ans),
        "explanation": exp,
        "explanation_summary": "",
        "explanation_correct": "",
        "explanation_choices": "",
        "explanation_point": "",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="eisei2_original_questions.csv → practice_questions.csv")
    ap.add_argument("--source", type=Path, default=SOURCE)
    ap.add_argument("--output", type=Path, default=OUTPUT)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-backup", action="store_true")
    args = ap.parse_args()

    if not args.source.is_file():
        print(f"error: {args.source} がありません", file=sys.stderr)
        return 1

    rows_out: list[dict[str, str]] = []
    with args.source.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            rows_out.append(row_to_practice(len(rows_out) + 1, row, i))

    if not rows_out:
        print("error: 取り込み行がありません", file=sys.stderr)
        return 1

    print(f"practice_questions: {len(rows_out)} 問（{args.source.name}）")
    if args.dry_run:
        return 0

    if args.output.is_file() and not args.no_backup:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = args.output.with_suffix(f".csv.bak.{ts}")
        shutil.copy2(args.output, backup)
        print(f"backup: {backup.name}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows_out)
    print(f"wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
