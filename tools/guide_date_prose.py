#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ガイド記事 prose の日付·時刻表記ルール（具体性と年度変動のバランス）。"""

from __future__ import annotations

import re

from tools.editorial_quality import norm

# カレンダー上の具体日（年度で変わりやすい）
CALENDAR_DATE_RE = re.compile(
    r"(?:"
    r"\d{4}年\d{1,2}月\d{1,2}日(?:（[日月火水木金土]）)?"
    r"|\d{1,2}月\d{1,2}日(?:（[日月火水木金土]）)?(?:\s*13:30(?:開始)?)?"
    r"|\d{1,2}/\d{1,2}(?:（[日月火水木金土]）)?"
    r"|\d{4}-\d{2}-\d{2}"
    r")"
)

EXAM_DAY_COMPACT_RE = re.compile(
    r"2026年度例10月11日（日）13:30(?:開始)?|10月11日（日）13:30(?:開始)?"
)

# 日程を多めに残してよい slug（試験日·申込·当日系）
SCHEDULE_HEAVY_SLUGS = frozenset(
    {
        "exam-schedule",
        "shiken-nittei",
        "exam-application-flow",
        "application-deadline-checklist",
        "exam-day-flow",
        "exam-day-items",
        "exam-day-time-allocation",
        "exam-day-troubleshooting",
        "shiken-tojitsu-nagare",
        "shiken-tojitsu-mochimono",
        "shiken-kaijo",
        "mental-prep-exam-day",
        "final-day-checklist",
        "final-week-prep",
        "final-mock-last-run",
        "pass-announcement-guide",
        "registration-after-pass",
        "after-pass-procedure",
        "menkyo-shinsei",
        "reschedule-and-absence",
        "retake-schedule-adjustment",
        "jisshi-moshikomi-tejun",
    }
)

SCHEDULE_HEAVY_PREFIXES = ("exam-day-", "final-", "shiken-tojitsu")

# 列ごとのカレンダー日上限（表行内は別カウント）
DEFAULT_MAX_DATES: dict[str, int] = {
    "lead": 2,
    "user_intent": 1,
    "meta_description": 0,
    "action_items": 0,
    "key_points": 0,
}
SECTION_BODY_MAX = 2
FAQ_ANSWER_MAX = 2

RELATIVE_REPLACEMENTS = (
    "1週間後",
    "次の演習日",
    "翌週",
    "次回",
)


def is_schedule_heavy_slug(slug: str) -> bool:
    if slug in SCHEDULE_HEAVY_SLUGS:
        return True
    return slug.startswith(SCHEDULE_HEAVY_PREFIXES)


def max_dates_for(slug: str, col: str) -> int:
    if is_schedule_heavy_slug(slug):
        if col == "lead":
            return 4
        if col.startswith("section_") and col.endswith("_body"):
            return 4
        if col.startswith("faq_") and col.endswith("_answer"):
            return 3
        return DEFAULT_MAX_DATES.get(col, 2)
    if col.startswith("section_") and col.endswith("_body"):
        return SECTION_BODY_MAX
    if col.startswith("faq_") and col.endswith("_answer"):
        return FAQ_ANSWER_MAX
    return DEFAULT_MAX_DATES.get(col, 1)


def _line_at(text: str, pos: int) -> str:
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    if end < 0:
        end = len(text)
    return text[start:end]


def count_calendar_dates(text: str, *, skip_table_rows: bool = True) -> int:
    t = norm(text)
    if not t:
        return 0
    n = 0
    for m in CALENDAR_DATE_RE.finditer(t):
        if skip_table_rows and _line_at(t, m.start()).lstrip().startswith("|"):
            continue
        n += 1
    return n


def _collapse_date_chains(text: str) -> str:
    """「6/18に…6/25に…7/6に」等の連鎖を1例に圧縮。"""
    out = text
    out = re.sub(
        r"(?:たとえば|例えば)?\d{1,2}/\d{1,2}(?:（[日月火水木金土]）)?に[^、。；;]{0,48}[、，]",
        "",
        out,
        count=0,
    )
    out = re.sub(
        r"(?:たとえば|例えば)?\d{1,2}月\d{1,2}日(?:（[日月火水木金土]）)?(?:に|から)[^、。；;]{0,48}[、，]",
        "",
        out,
        count=0,
    )
    out = re.sub(
        r"「[^」]*(?:→|→)[^」]*」",
        "「受験→合格→免許→選任」の流れ",
        out,
    )
    out = re.sub(r"[。]{2,}", "。", out)
    return out


def trim_calendar_dates(text: str, *, max_dates: int, col: str = "") -> str:
    """表行は維持し、prose 内の具体日を上限まで削る（残りは相対表現）。"""
    if not text or max_dates < 0:
        return text
    out = text
    if col in {"lead", "user_intent"}:
        out = _collapse_date_chains(out)
    if max_dates == 0:
        # action_items 等：具体日→相対
        def _zero_repl(m: re.Match[str]) -> str:
            if _line_at(out, m.start()).lstrip().startswith("|"):
                return m.group(0)
            return RELATIVE_REPLACEMENTS[0]

        return CALENDAR_DATE_RE.sub(_zero_repl, out)

    kept = 0
    rel_idx = 0
    parts: list[str] = []
    last = 0
    for m in CALENDAR_DATE_RE.finditer(out):
        if _line_at(out, m.start()).lstrip().startswith("|"):
            continue
        kept += 1
        parts.append(out[last : m.start()])
        if kept <= max_dates:
            parts.append(m.group(0))
        else:
            repl = RELATIVE_REPLACEMENTS[rel_idx % len(RELATIVE_REPLACEMENTS)]
            rel_idx += 1
            parts.append(repl)
        last = m.end()
    parts.append(out[last:])
    result = "".join(parts)
    # 試験日ブロックは1回だけ（lead 向け）
    if col == "lead":
        seen_exam = False

        def _exam_once(m: re.Match[str]) -> str:
            nonlocal seen_exam
            if seen_exam:
                return "試験日（要項で再確認）"
            seen_exam = True
            return m.group(0)

        result = EXAM_DAY_COMPACT_RE.sub(_exam_once, result)
    return result


def soften_dates_for_column(text: str, *, slug: str, col: str) -> str:
    if not text:
        return text
    limit = max_dates_for(slug, col)
    return trim_calendar_dates(text, max_dates=limit, col=col)


def audit_date_density(slug: str, patch: dict[str, str]) -> list[str]:
    """監査用：上限超過の警告。"""
    warnings: list[str] = []
    cols = (
        ["lead", "user_intent", "meta_description", "action_items"]
        + [f"section_{n}_body" for n in range(1, 8)]
        + [f"faq_{n}_answer" for n in range(1, 5)]
    )
    for col in cols:
        val = norm(patch.get(col))
        if not val:
            continue
        limit = max_dates_for(slug, col)
        n = count_calendar_dates(val)
        if n > limit:
            warnings.append(f"{slug}:{col} calendar_dates={n} max={limit}")
    return warnings
