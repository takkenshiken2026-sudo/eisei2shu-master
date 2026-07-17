#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eisei2 過去問・オリジナル CSV から選択肢別解説・学習ヒントを生成し、
data/eisei2_past_explanation_meta.csv に書き出す。

使い方:
  python3 tools/enrich_eisei2_past_explanations.py
  python3 tools/enrich_eisei2_past_explanations.py --dry-run

生成後:
  python3 tools/build_question_pages.py
"""

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

from enrich_past_explanation_choices import build_row_fields, choice_texts, norm

GENERIC_WRONG_MARK = "出題趣旨・問題文の条件に照らすと正答"

# 抽出時に先頭の判定節が「（N）節 (N)節…」と全角→半角括弧で重複してしまう
# ケースがある。冗長な先頭エコーを取り除き、2番目（本文につながる方）を残す。
_LEADING_ECHO_RE = re.compile(r"^\s*（(\d)）(.{3,70}?)\s*\(\1\)\2")


def strip_leading_echo(text: str) -> str:
    if not text:
        return text
    m = _LEADING_ECHO_RE.match(text)
    if not m:
        return text
    second = text.find(f"({m.group(1)})", m.start(2))
    if second <= 0:
        return text
    return text[second:].lstrip()

DEFAULT_OUT = ROOT / "data" / "eisei2_past_explanation_meta.csv"
META_FIELDS = [
    "開催年数",
    "開催月",
    "問番号",
    "科目",
    "explanation_summary",
    "explanation_correct",
    "explanation_choices",
    "explanation_point",
]

CATEGORY_HINTS: dict[str, str] = {
    "関係法令": (
        "労働安全衛生法・労働基準法などは、数字（人数・日数・年齢）と義務の主体をセットで整理すると得点しやすくなります。"
        "関連用語は用語解説で押さえ、同年・前後の過去問で選任・報告・届出の区別を確認してください。"
    ),
    "労働衛生": (
        "化学物質・粉じん・騒音などは、管理区分・測定・保護具の要件を表にまとめると復習が効率的です。"
        "用語解説で物質名と管理濃度を確認したうえで、類似テーマの過去問を連続して解いてください。"
    ),
    "労働生理": (
        "温度・湿度・作業強度・WBGT などは、基準値と測定・対策の手順を一連の流れで覚えると理解が定着します。"
        "生理・環境の用語を押さえたあと、数値を問う過去問で計算・判断の練習を重ねてください。"
    ),
}

KEYWORD_HINTS: list[tuple[tuple[str, ...], str]] = [
    (
        ("衛生管理者", "衛生委員会"),
        "選任人数・専任・報告書の提出先は混同しやすいので、用語解説の表と関連過去問で区別してください。",
    ),
    (
        ("産業医",),
        "産業医の選任期限・業務・衛生管理者との別義務を、条文の趣旨と数字でセット復習してください。",
    ),
    (
        ("作業主任者", "作業指揮者"),
        "該当作業の範囲と選任要件は組合せ問題でも出題されるため、作業ごとの一覧表を作るとよいです。",
    ),
    (
        ("有機溶剤", "特定化学物質", "化学物質", "粉じん", "石綿"),
        "管理区分・記録・測定・保護具の要件は物質ごとに比較表にまとめ、誤りを問う設問では各肢を単独で検証してください。",
    ),
    (
        ("WBGT", "暑熱", "温度", "湿度", "作業強度"),
        "基準値・測定方法・対策の順で整理し、数値問題は単位と条件（屋内・屋外など）をメモしながら解き直してください。",
    ),
    (
        ("騒音", "振動", "レーザー", "電離放射線"),
        "測定・管理区分・保護具・記録の義務は分野ごとに共通点と相違点を表にすると定着しやすくなります。",
    ),
    (
        ("健康診断", "人間ドック", "雇入れ時", "特殊健康診断"),
        "実施時期・対象者・項目・事後措置は頻出なので、時系列のチェックリストで復習してください。",
    ),
    (
        ("リスクアセスメント", "危険予知"),
        "手順（把握・見積・低減）と記録の要否を、問題文のキーワードと照らして確認してください。",
    ),
]


def meta_key(row: dict) -> tuple[str, str, str, str]:
    return (
        norm(row.get("開催年数")),
        norm(row.get("開催月")),
        norm(str(row.get("問番号") or "")),
        norm(row.get("科目")),
    )


def eisei2_to_enrich_row(row: dict) -> dict:
    opts = [(row.get(f"({i})") or "").strip() for i in range(1, 6)]
    return {
        "stem": norm(row.get("問")),
        "choice_1": opts[0],
        "choice_2": opts[1],
        "choice_3": opts[2],
        "choice_4": opts[3],
        "choice_5": opts[4],
        "correct": norm(row.get("正答番号")),
        "explanation": norm(row.get("解説")),
        "category": norm(row.get("科目")),
        "explanation_summary": "",
        "explanation_correct": "",
    }


def build_explanation_point(category: str, stem: str, exp: str) -> str:
    parts: list[str] = []
    base = CATEGORY_HINTS.get(category, "")
    if base:
        parts.append(base)
    text = f"{stem} {exp}"
    for keywords, hint in KEYWORD_HINTS:
        if any(k in text for k in keywords):
            if hint not in parts:
                parts.append(hint)
            if len(parts) >= 2:
                break
    if "適切でない" in stem or "誤っている" in stem or "誤り" in stem:
        neg = (
            "「最も適切でないもの」「誤っているもの」を問う設問では、"
            "各選択肢を単独の真偽で確認し、一見正しそうな肢に注意してください。"
        )
        if neg not in parts:
            parts.append(neg)
    elif "正しい" in stem and "誤" not in stem[:30]:
        pos = (
            "「正しいもの」を問う設問では、数字・期限・主体（誰が・何を）の"
            "ずれがないか、各肢を条文イメージと照合してください。"
        )
        if pos not in parts:
            parts.append(pos)
    return " ".join(parts[:3])


def postprocess_choice_notes(
    choices_field: str,
    *,
    stem: str,
    exp: str,
    correct: int,
    enrich_in: dict,
) -> str:
    if not choices_field or GENERIC_WRONG_MARK not in choices_field:
        return choices_field
    texts = choice_texts(enrich_in)
    exp_lead = (exp.split("。")[0] + "。") if exp else ""
    find_false = any(k in stem for k in ("誤っている", "適切でない", "誤り"))
    find_true = "正しい" in stem and not find_false
    out: list[str] = []
    for item in choices_field.split(";"):
        if ":" not in item:
            continue
        n_s, note = item.split(":", 1)
        try:
            n = int(n_s)
        except ValueError:
            out.append(item)
            continue
        if GENERIC_WRONG_MARK not in note:
            out.append(item)
            continue
        opt = texts.get(n, "")
        opt_short = opt[:72] + ("…" if len(opt) > 72 else "")
        if find_false:
            note = (
                f"（{n}）「{opt_short}」は、単独の記述として正しい内容に見える場合がありますが、"
                f"本問は誤っているものを選ぶ設問です。正答は（{correct}）です。"
                f" {exp_lead}"
            )
        elif find_true:
            note = (
                f"（{n}）「{opt_short}」は、問題文の趣旨・法令の要件に照らすと正しい記述ではありません。"
                f"正答は（{correct}）です。 {exp_lead}"
            )
        else:
            note = (
                f"（{n}）「{opt_short}」は本問の正答（{correct}）とは異なります。"
                f" {exp_lead}"
            )
        out.append(f"{n}:{note}")
    return ";".join(out)


def enrich_one(row: dict) -> dict:
    enrich_in = eisei2_to_enrich_row(row)
    choices_field, correct_body, summary, _enrich_point = build_row_fields(enrich_in)
    try:
        correct_n = int(enrich_in["correct"])
    except (TypeError, ValueError):
        correct_n = 0
    if correct_n and choices_field:
        choices_field = postprocess_choice_notes(
            choices_field,
            stem=norm(row.get("問")),
            exp=norm(row.get("解説")),
            correct=correct_n,
            enrich_in=enrich_in,
        )
    category = norm(row.get("科目"))
    stem = norm(row.get("問"))
    exp = norm(row.get("解説"))
    point = build_explanation_point(category, stem, exp)
    for bad in (
        " この記述は本問の正答ではありません。",
        "本問の正答ではありません",
        "正答ではありません",
    ):
        correct_body = correct_body.replace(bad, "")
    correct_body = re.sub(r"\s{2,}", " ", correct_body).strip()
    summary = strip_leading_echo(summary)
    correct_body = strip_leading_echo(correct_body)

    return {
        "開催年数": norm(row.get("開催年数")),
        "開催月": norm(row.get("開催月")),
        "問番号": norm(str(row.get("問番号") or "")),
        "科目": category,
        "explanation_summary": summary,
        "explanation_correct": correct_body,
        "explanation_choices": choices_field,
        "explanation_point": point,
    }


def load_csv_paths() -> list[Path]:
    data = ROOT / "data"
    paths = [
        data / "eisei2_past_questions.csv",
        data / "eisei2_original_questions.csv",
    ]
    return [p for p in paths if p.is_file()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    paths = load_csv_paths()
    if not paths:
        print("error: no eisei2 CSV found under data/", file=sys.stderr)
        return 1

    out_rows: list[dict] = []
    short = 0
    for path in paths:
        rows = list(csv.DictReader(path.read_text(encoding="utf-8-sig").splitlines()))
        for row in rows:
            if not norm(row.get("問")):
                continue
            meta = enrich_one(row)
            ec = meta.get("explanation_choices") or ""
            if ec:
                notes = [p.split(":", 1)[1] for p in ec.split(";") if ":" in p]
                if notes and sum(len(n) for n in notes) / len(notes) < 36:
                    short += 1
            out_rows.append(meta)

    filled = sum(1 for r in out_rows if r.get("explanation_choices"))
    print(f"rows={len(out_rows)} explanation_choices filled={filled}")
    if short:
        print(f"warning: {short} rows with short average wrong-note length")

    if args.dry_run:
        if out_rows:
            s = out_rows[0].get("explanation_choices", "")[:240]
            print("sample:", s)
            print("point:", out_rows[0].get("explanation_point", "")[:120])
        return 0

    out_path = args.out.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=META_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
