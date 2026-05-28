"""用語記事の品質判定・自動充実ヘルパ。"""
from __future__ import annotations

import re

GENERIC_EXAM_MARKERS: tuple[str, ...] = (
    "の定義・数値を類似語と混同",
    "は単独で完結する制度",
    "は努力規定のみ」→",
    "関連規則・手順とセットで復習",
)


def is_generic_exam_points(text: str) -> bool:
    ep = (text or "").strip()
    if not ep:
        return True
    return any(m in ep for m in GENERIC_EXAM_MARKERS)


def is_thin_row(row: dict) -> bool:
    td = (row.get("term_detail_body") or "").strip()
    sd = (row.get("short_def") or "").strip()
    expl = (row.get("explanation") or "").strip()
    if td and sd and td == sd and len(td) < 120:
        return True
    if expl and sd and expl == sd and len(expl) < 120:
        return True
    if not td and len(sd) < 80:
        return True
    return False


def md_needs_upgrade(md_text: str) -> bool:
    if not md_text or "##" not in md_text:
        return True
    if "定義の整理" in md_text and md_text.count("##") <= 3:
        return True
    if "試験で狙われる頻出ポイント" in md_text and md_text.count("|") < 6:
        return True
    return False


def md_quality_ok(md_text: str) -> bool:
    if not md_text:
        return False
    h2_count = len(re.findall(r"^## ", md_text, re.MULTILINE))
    table_rows = len(re.findall(r"^\|", md_text, re.MULTILINE))
    if h2_count >= 4 and table_rows >= 4:
        return True
    if h2_count >= 3 and table_rows >= 8:
        return True
    if "試験での整理" in md_text and table_rows >= 6:
        return True
    return False


def tips_to_comparison_table(tips: list[str]) -> list[list[str]]:
    rows: list[list[str]] = [["よくある誤り", "正しい整理"]]
    for tip in tips[:4]:
        tip = tip.strip()
        if "→" in tip:
            left, right = tip.split("→", 1)
            rows.append([left.strip("「」 "), right.strip()])
        else:
            rows.append([tip, "条文・数値で確認"])
    return rows


def expand_explanation(term: str, category: str, short_def: str, tips: list[str]) -> str:
    base = (short_def or f"{term}に関する制度・測定・措置の要点").strip()
    lead = f"{term}は衛生管理者試験の{category}で扱う用語です。"
    body = base if base.endswith("。") else base + "。"
    extra = ""
    if tips:
        t0 = tips[0]
        if "→" in t0:
            wrong = t0.split("→", 1)[0].strip("「」 ")
            extra = f" 出題では「{wrong}」のような誤り肢に注意し、関連する法令・手順とセットで整理してください。"
        else:
            extra = f" 出題では{t0[:40]}…のような言い換えに注意します。"
    text = (lead + body + extra).strip()
    return text[:320]


def auto_sections(term: str, category: str, short_def: str, tips: list[str]) -> list:
    overview = [
        ["観点", "内容"],
        ["用語", term],
        ["分野", category],
        ["要点", short_def or f"{term}の定義と試験頻出の整理"],
    ]
    sections: list = [("試験での整理", overview)]
    if tips:
        sections.append(("比較・注意（頻出）", tips_to_comparison_table(tips)))
        sections.append(("試験で狙われる頻出ポイント", tips))
    return sections
