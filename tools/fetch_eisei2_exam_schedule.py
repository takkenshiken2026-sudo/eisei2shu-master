#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""安全衛生技術試験協会の第二種衛生管理者試験日程ページから CSV を生成する。"""

from __future__ import annotations

import csv
import re
import sys
import urllib.request
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SOURCE_URL = "https://www.exam.or.jp/schedule/h_nittei502/"
OUTPUT_CSV = ROOT / "data" / "exam_schedule_eisei2.csv"

VENUE_REGION: dict[str, str] = {
    "eisei-hokkaido": "北海道",
    "eisei-tohoku": "東北",
    "eisei-kanto": "関東",
    "eisei-tokyo": "関東",
    "eisei-chubu": "中部",
    "eisei-kinki": "近畿",
    "eisei-osaka": "近畿",
    "eisei-chushi": "中国・四国",
    "eisei-kyushu": "九州",
}

WEEKDAY_JA = ("月", "火", "水", "木", "金", "土", "日")


def fetch_html() -> str:
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "eisei2shu-master-schedule-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", "replace")


def month_year(period_title: str, month: int) -> int:
    """令和8/9年度の期間表記から西暦年を返す。"""
    if month >= 4:
        return 2026
    if "R9" in period_title or "９" in period_title:
        return 2027
    return 2026


def parse_day_tokens(cell_html: str) -> list[tuple[int, bool]]:
    """セル HTML から (日, 土日祝フラグ) のリスト。"""
    chunks = re.split(r"<br\s*/?>", cell_html, flags=re.I)
    out: list[tuple[int, bool]] = []
    for chunk in chunks:
        is_red = bool(re.search(r'color\s*=\s*["\']?red', chunk, re.I))
        text = re.sub(r"<[^>]+>", "", chunk).strip()
        if not text:
            continue
        for m in re.finditer(r"\d+", text):
            out.append((int(m.group()), is_red))
    return out


def parse_schedule(html: str) -> list[dict[str, str]]:
    fetched_at = datetime.now().strftime("%Y-%m-%d")
    parts = re.split(r'<h2 id="(eisei-[^"]+)">([^<]+)</h2>', html)
    rows: list[dict[str, str]] = []
    for i in range(1, len(parts), 3):
        venue_id = parts[i].strip()
        venue_name = parts[i + 1].strip()
        block = parts[i + 2]
        region = VENUE_REGION.get(venue_id, "")
        period_blocks = re.findall(
            r"<h4>(令和[^<]+)</h4>\s*<table>(.*?)</table>",
            block,
            flags=re.S,
        )
        for period_raw, table_html in period_blocks:
            period_title = re.sub(r"<[^>]+>", "", period_raw).strip()
            month_headers = re.findall(r"<th[^>]*>(\d+月)</th>", table_html)
            day_row = re.search(
                r"実施日</td>\s*(.*?)(?:</tr>|</tbody>)",
                table_html,
                flags=re.S,
            )
            if not day_row:
                continue
            day_cells = re.findall(r"<td[^>]*>(.*?)</td>", day_row.group(1), flags=re.S)
            for month_label, cell in zip(month_headers, day_cells):
                month = int(re.sub(r"\D", "", month_label))
                year = month_year(period_title, month)
                for day_num, is_red in parse_day_tokens(cell):
                    try:
                        d = date(year, month, day_num)
                    except ValueError:
                        continue
                    weekday = WEEKDAY_JA[d.weekday()]
                    weekend = is_red or d.weekday() >= 5
                    rows.append(
                        {
                            "venue_id": venue_id,
                            "venue_name": venue_name,
                            "region": region,
                            "period_label": period_title,
                            "exam_date": d.isoformat(),
                            "weekday_ja": weekday,
                            "weekend_or_holiday": "1" if weekend else "0",
                            "source_url": SOURCE_URL,
                            "fetched_at": fetched_at,
                        }
                    )
    rows.sort(key=lambda r: (r["exam_date"], r["venue_name"]))
    return rows


def write_csv(rows: list[dict[str, str]]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "venue_id",
        "venue_name",
        "region",
        "period_label",
        "exam_date",
        "weekday_ja",
        "weekend_or_holiday",
        "source_url",
        "fetched_at",
    ]
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    html = fetch_html()
    rows = parse_schedule(html)
    if not rows:
        print("ERROR: 試験日データを取得できませんでした", file=sys.stderr)
        return 1
    write_csv(rows)
    venues = len({r["venue_id"] for r in rows})
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)} ({len(rows)} dates, {venues} venues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
