#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""試験日程 CSV から検索 UI・一覧表・公式風カレンダー表を生成する。"""

from __future__ import annotations

import csv
import html
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MONTH_LABELS = ("1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月")

VENUE_DISPLAY_ORDER = (
    "eisei-hokkaido",
    "eisei-tohoku",
    "eisei-kanto",
    "eisei-tokyo",
    "eisei-chubu",
    "eisei-kinki",
    "eisei-osaka",
    "eisei-chushi",
    "eisei-kyushu",
)


def load_schedule_rows(csv_path: Path | None = None) -> list[dict[str, str]]:
    from tools.site_config import exam_schedule_csv_path

    path = csv_path or exam_schedule_csv_path()
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def latest_fetched_at(rows: list[dict[str, str]]) -> str:
    dates = [str(r.get("fetched_at") or "").strip() for r in rows if r.get("fetched_at")]
    return max(dates) if dates else ""


def _format_display_date(iso: str) -> str:
    try:
        d = datetime.strptime(iso, "%Y-%m-%d")
    except ValueError:
        return iso
    return f"{d.year}年{d.month}月{d.day}日"


def _venue_order(rows: list[dict[str, str]]) -> list[tuple[str, str, str]]:
    seen: dict[str, tuple[str, str]] = {}
    for row in rows:
        vid = row.get("venue_id") or ""
        if vid and vid not in seen:
            seen[vid] = (row.get("venue_name") or vid, row.get("region") or "")
    ordered_ids = [vid for vid in VENUE_DISPLAY_ORDER if vid in seen]
    for vid in seen:
        if vid not in ordered_ids:
            ordered_ids.append(vid)
    return [(vid, seen[vid][0], seen[vid][1]) for vid in ordered_ids]


def exam_schedule_tools_html(rows: list[dict[str, str]]) -> str:
    venues = _venue_order(rows)
    venue_options = "".join(
        f'<li class="exam-schedule-pref-option" role="option" data-value="{html.escape(vid)}" '
        f'data-label="{html.escape(name)}">{html.escape(name)}</li>'
        for vid, name, _region in venues
    )
    region_chips = "".join(
        f'<button type="button" class="exam-schedule-region-chip" data-region="{html.escape(region)}">'
        f"{html.escape(region)}</button>"
        for region in sorted({r.get("region") or "" for r in rows if r.get("region")})
    )
    return f"""<section class="exam-schedule-table-section" aria-labelledby="exam-schedule-tools-title">
<h2 class="u-visually-hidden" id="exam-schedule-tools-title">試験日の絞り込み</h2>
<p class="exam-schedule-table-note">会場名・地域・年月で絞り込めます。<strong class="exam-schedule-weekend-mark">赤字</strong>は土日祝日に実施する試験日です（公式ページと同じ表記）。最新の変更は必ず<a href="https://www.exam.or.jp/schedule/h_nittei502/" target="_blank" rel="noopener noreferrer">安全衛生技術試験協会の日程ページ</a>で確認してください。</p>
<div class="exam-schedule-table-tools">
<label class="exam-schedule-sort-label" for="exam-schedule-sort">並び順</label>
<select id="exam-schedule-sort" class="exam-schedule-sort-select" aria-label="並び順">
<option value="date-asc">試験日が近い順</option>
<option value="date-desc">試験日が遠い順</option>
<option value="venue">会場名順</option>
</select>
<div class="exam-schedule-pref-combobox" id="exam-schedule-venue-box">
<span class="exam-schedule-pref-label" id="exam-schedule-venue-label">会場</span>
<div class="exam-schedule-pref-combobox-field">
<input type="search" id="exam-schedule-venue-input" class="exam-schedule-pref-input"
  role="combobox" aria-expanded="false" aria-controls="exam-schedule-venue-list"
  aria-autocomplete="list" aria-labelledby="exam-schedule-venue-label"
  placeholder="会場名で検索（例：東京）" autocomplete="off">
<button type="button" class="exam-schedule-pref-clear hide" id="exam-schedule-venue-clear" aria-label="会場をクリア">×</button>
<button type="button" class="exam-schedule-pref-toggle" id="exam-schedule-venue-toggle" aria-label="会場一覧を開く"></button>
<ul class="exam-schedule-pref-listbox hide" id="exam-schedule-venue-list" role="listbox" aria-labelledby="exam-schedule-venue-label">
<li class="exam-schedule-pref-option on" role="option" data-value="" data-label="すべて">すべて</li>
{venue_options}
</ul>
</div>
</div>
<label class="exam-schedule-sort-label" for="exam-schedule-month">年月</label>
<input type="month" id="exam-schedule-month" class="exam-schedule-month-input" aria-label="年月で絞り込み">
<span class="exam-schedule-table-count" id="exam-schedule-count" aria-live="polite"></span>
</div>
<div class="exam-schedule-region-chips" role="group" aria-label="地域で絞り込み">
<button type="button" class="exam-schedule-region-chip on" data-region="">すべて</button>
{region_chips}
</div>
<p class="exam-schedule-table-empty hide" id="exam-schedule-empty">条件に一致する試験日がありません。絞り込みを解除するか、別の会場・年月をお試しください。</p>
<div class="exam-schedule-table-wrap">
<table class="seo-info-table exam-schedule-list-table" id="exam-schedule-list">
<thead><tr>
<th scope="col">試験日</th>
<th scope="col">曜日</th>
<th scope="col">会場</th>
<th scope="col">地域</th>
</tr></thead>
<tbody>
{exam_schedule_list_rows_html(rows)}
</tbody>
</table>
</div>
<script type="application/json" id="exam-schedule-data">{json.dumps(rows, ensure_ascii=False)}</script>
</section>"""


def exam_schedule_list_rows_html(rows: list[dict[str, str]]) -> str:
    parts: list[str] = []
    for row in rows:
        iso = row.get("exam_date") or ""
        weekend = row.get("weekend_or_holiday") == "1"
        weekday = row.get("weekday_ja") or ""
        venue = row.get("venue_name") or ""
        region = row.get("region") or ""
        vid = row.get("venue_id") or ""
        date_cls = "exam-schedule-date weekend" if weekend else "exam-schedule-date"
        weekday_cls = "exam-schedule-weekday weekend" if weekend else "exam-schedule-weekday"
        parts.append(
            f'<tr data-date="{html.escape(iso)}" data-venue-id="{html.escape(vid)}" '
            f'data-region="{html.escape(region)}" data-venue-name="{html.escape(venue)}">'
            f'<td><span class="{date_cls}">{html.escape(_format_display_date(iso))}</span></td>'
            f'<td><span class="{weekday_cls}">{html.escape(weekday)}</span></td>'
            f"<td>{html.escape(venue)}</td>"
            f"<td>{html.escape(region)}</td>"
            f"</tr>"
        )
    return "\n".join(parts)


def _calendar_months_for_period(period_label: str) -> list[int]:
    if "R8.10" in period_label or "R8.10" in period_label.replace("８", "8"):
        return list(range(10, 13)) + list(range(1, 4))
    return list(range(4, 10))


def exam_schedule_calendar_html(rows: list[dict[str, str]]) -> str:
    """公式ページ風の会場別カレンダー表。"""
    by_venue: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_venue[row.get("venue_id") or ""].append(row)

    blocks: list[str] = []
    for vid, vname, region in _venue_order(rows):
        venue_rows = by_venue.get(vid, [])
        if not venue_rows:
            continue
        by_period: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in venue_rows:
            by_period[row.get("period_label") or ""].append(row)

        period_html: list[str] = []
        for period_label in sorted(by_period.keys()):
            period_rows = by_period[period_label]
            months = _calendar_months_for_period(period_label)
            month_cells: list[str] = []
            for month in months:
                days = [
                    r
                    for r in period_rows
                    if datetime.strptime(r["exam_date"], "%Y-%m-%d").month == month
                ]
                day_spans = []
                for r in sorted(days, key=lambda x: x["exam_date"]):
                    day_num = datetime.strptime(r["exam_date"], "%Y-%m-%d").day
                    cls = "exam-schedule-cal-day weekend" if r.get("weekend_or_holiday") == "1" else "exam-schedule-cal-day"
                    day_spans.append(f'<span class="{cls}">{day_num}</span>')
                month_cells.append(
                    f'<td>{"".join(day_spans) if day_spans else "—"}</td>'
                )
            month_headers = "".join(f"<th>{m}月</th>" for m in months)
            period_html.append(
                f'<h3 class="exam-schedule-period-title">{html.escape(period_label)}</h3>'
                f'<div class="exam-schedule-calendar-wrap"><table class="exam-schedule-calendar-grid">'
                f"<thead><tr><th scope=\"col\">実施月</th>{month_headers}</tr></thead>"
                f'<tbody><tr><th scope="row">実施日</th>{"".join(month_cells)}</tr></tbody>'
                f"</table></div>"
            )

        blocks.append(
            f'<section class="exam-schedule-venue-block" id="{html.escape(vid)}" '
            f'data-venue-id="{html.escape(vid)}" data-region="{html.escape(region)}">'
            f'<h2 class="exam-schedule-venue-title">{html.escape(vname)}'
            f'<span class="exam-schedule-venue-region">{html.escape(region)}</span></h2>'
            f"{''.join(period_html)}"
            f"</section>"
        )

    jump_nav = "".join(
        f'<a class="exam-schedule-venue-chip" href="#{html.escape(vid)}">{html.escape(vname.replace("安全衛生技術センター", "").replace("試験場", "試験場"))}</a>'
        for vid, vname, _region in _venue_order(rows)
    )
    short_names = {
        "北海道安全衛生技術センター": "北海道",
        "東北安全衛生技術センター": "東北",
        "関東安全衛生技術センター": "関東",
        "東京試験場": "東京試験場",
        "中部安全衛生技術センター": "中部",
        "近畿安全衛生技術センター": "近畿",
        "大阪試験場": "大阪試験場",
        "中国四国安全衛生技術センター": "中国四国",
        "九州安全衛生技術センター": "九州",
    }
    jump_nav = "".join(
        f'<a class="exam-schedule-venue-chip" href="#{html.escape(vid)}">{html.escape(short_names.get(vname, vname))}</a>'
        for vid, vname, _region in _venue_order(rows)
    )
    return (
        f'<nav class="exam-schedule-venue-nav" aria-label="会場へジャンプ">{jump_nav}</nav>'
        f'<div class="exam-schedule-calendar-section">{"".join(blocks)}</div>'
    )


def exam_schedule_table_html(
    rows: list[dict[str, str]],
    *,
    section_num: int | None = 1,
    show_heading: bool = True,
    show_note: bool = True,
    show_calendar: bool = True,
) -> str:
    if not rows:
        return '<p class="exam-schedule-table-note">試験日程データがありません。</p>'
    parts = [exam_schedule_tools_html(rows)]
    if show_calendar:
        parts.append(exam_schedule_calendar_html(rows))
    return "\n".join(parts)
