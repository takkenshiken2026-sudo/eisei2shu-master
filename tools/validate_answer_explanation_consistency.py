#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""正答番号と解説本文・解説メタの整合性を検査する。"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
ROOT = _TOOLS.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from enrich_eisei2_past_explanations import meta_key
from enrich_past_explanation_choices import norm
from q_explanation import question_ask_mode

FORBIDDEN_IN_CORRECT = (
    "本問の正答ではありません",
    "正答ではありません",
)


def extract_stated_answer(exp: str) -> list[int]:
    found: list[int] = []
    for pat in (
        r"正答は\s*[（(]?([1-5])[）)]?",
        r"正解は\s*[（(]?([1-5])[）)]?",
    ):
        for m in re.finditer(pat, exp):
            n = int(m.group(1))
            if n not in found:
                found.append(n)
    return found


def check_row(row: dict, meta_row: dict | None) -> list[str]:
    issues: list[str] = []
    try:
        correct = int(norm(row.get("正答番号")))
    except (TypeError, ValueError):
        return ["正答番号が不正"]
    if not 1 <= correct <= 5:
        return [f"正答番号が範囲外: {correct}"]

    stem = norm(row.get("問"))
    exp = norm(row.get("解説"))
    mode = question_ask_mode(stem)
    key = f"{row.get('開催年数')} {row.get('開催月')} 問{row.get('問番号')} {row.get('科目')}"

    for n in extract_stated_answer(exp):
        if n != correct:
            issues.append(f"解説本文が正答{n}と述べているがCSV正答は{correct}")

    if mode == "most_correct":
        for pat in (
            rf"（{correct}）[^。]{{0,80}}(?:誤り|正しくない|不適切)",
            rf"\({correct}\)[^。]{{0,80}}(?:誤り|正しくない|不適切)",
        ):
            if re.search(pat, exp):
                issues.append(f"「正しいもの」設問で正答肢（{correct}）を誤りとしている")
                break

    if meta_row:
        ec = norm(meta_row.get("explanation_correct"))
        if ec:
            for bad in FORBIDDEN_IN_CORRECT:
                if bad in ec:
                    issues.append(f"explanation_correctに矛盾語句「{bad}」")
                    break
            for n in extract_stated_answer(ec):
                if n != correct:
                    issues.append(
                        f"explanation_correctが正答{n}と述べているがCSV正答は{correct}"
                    )

        choices_raw = norm(meta_row.get("explanation_choices"))
        if choices_raw:
            for item in choices_raw.split(";"):
                if ":" not in item:
                    continue
                n_s, _note = item.split(":", 1)
                try:
                    n = int(n_s)
                except ValueError:
                    continue
                if n == correct:
                    issues.append(f"explanation_choicesに正答肢（{correct}）が含まれる")

    return [f"{key}: {msg}" for msg in issues]


def load_meta(path: Path) -> dict[tuple, dict]:
    if not path.is_file():
        return {}
    out: dict[tuple, dict] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            out[meta_key(row)] = row
    return out


def audit_csv(csv_path: Path, meta_path: Path) -> list[str]:
    meta = load_meta(meta_path)
    issues: list[str] = []
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            issues.extend(check_row(row, meta.get(meta_key(row))))
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--past-csv", default=str(ROOT / "data" / "eisei2_past_questions.csv"))
    ap.add_argument("--orig-csv", default=str(ROOT / "data" / "eisei2_original_questions.csv"))
    ap.add_argument("--meta-csv", default=str(ROOT / "data" / "eisei2_past_explanation_meta.csv"))
    args = ap.parse_args()

    all_issues: list[str] = []
    all_issues.extend(audit_csv(Path(args.past_csv), Path(args.meta_csv)))
    all_issues.extend(audit_csv(Path(args.orig_csv), Path(args.meta_csv)))

    if all_issues:
        print(f"不一致 {len(all_issues)} 件:\n")
        for i, msg in enumerate(all_issues, 1):
            print(f"{i}. {msg}")
        return 1
    print("不一致は検出されませんでした。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
