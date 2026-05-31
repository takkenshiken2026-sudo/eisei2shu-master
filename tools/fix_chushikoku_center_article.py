#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""chushikoku-center 記事の量産テンプレ崩れを修正する。"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SHELL = Path.home() / "Projects" / "exam-site-shell"
if str(SHELL) not in sys.path:
    sys.path.insert(0, str(SHELL))

from tools.archive.eisei2shu_guide_content_lib import (  # noqa: E402
    OFFICIAL,
    action_items_for,
    key_points_for,
    lead_for,
    meta_description_for,
    section_body_for,
    topic_from_row,
    user_intent_for,
)

CSV_PATH = ROOT / "data" / "guide_articles.csv"
TOPIC = "中国四国安全衛生技術センター"
SLUG = "chushikoku-center"
OFFICIAL_URL = "安全衛生技術試験協会（公式）|https://www.jissh.or.jp/"

SECTIONS = [
    ("基本情報", "section_1"),
    ("アクセス方法", "section_2"),
    ("試験日程の確認方法", "section_3"),
    ("申込の注意点", "section_4"),
    ("試験当日の持ち物", "section_5"),
    ("まとめ", "section_6"),
]

FAQ = [
    (
        "中国・四国で受験する人はこの記事を読むべきですか？",
        "中国・四国地方で第二種衛生管理者試験を受験する予定の方は、受験地選択と会場アクセスの確認に本記事が役立ちます。"
        "試験範囲の学習そのものは公式テキストと演習問題で進め、日程・会場・持ち物だけは安全衛生技術試験協会（公式）で最新情報を確認してください。",
    ),
    (
        "会場の住所やアクセスはどこで確認しますか？",
        f"会場の所在地・交通手段・アクセス方法は{OFFICIAL}の受験案内および中国四国安全衛生技術センターの案内ページで確認してください。"
        "試験日が近づいたら前日までにルートと所要時間を確定し、当日は開始時刻の30分前到着を目安に余裕を持って向かってください。",
    ),
    (
        "試験当日の持ち物は何を準備すればよいですか？",
        "受験要項および受験票に記載された持ち物（鉛筆・消しゴム・身分証など）を前日に準備してください。"
        "禁止物品（スマートフォン、参考書など）は要項どおりに守り、筆記用具は予備があると当日のトラブルを減らせます。",
    ),
]


def patch_row(row: dict[str, str], fieldnames: list[str]) -> dict[str, str]:
    row = {k: row.get(k, "") for k in fieldnames}
    row["title"] = f"{TOPIC}【アクセス・試験日程・第二種衛生管理者の受験情報】"
    row["meta_description"] = meta_description_for(row, TOPIC)
    row["lead"] = lead_for(row, TOPIC)
    row["user_intent"] = user_intent_for(TOPIC, row.get("genre") or "")
    row["action_items"] = action_items_for(TOPIC, SLUG, row.get("genre") or "")
    row["key_points"] = key_points_for(row, TOPIC)
    if "official_sources" in fieldnames:
        row["official_sources"] = OFFICIAL_URL

    ctx: dict = {}
    for idx, (heading, _prefix) in enumerate(SECTIONS, start=1):
        hcol = f"section_{idx}_heading"
        bcol = f"section_{idx}_body"
        if hcol in fieldnames:
            row[hcol] = heading
        if bcol in fieldnames:
            row[bcol] = section_body_for(heading, TOPIC, SLUG, row.get("genre") or "", ctx)

    for idx in range(7, 9):
        for suffix in ("heading", "body"):
            col = f"section_{idx}_{suffix}"
            if col in fieldnames:
                row[col] = ""

    for idx, (question, answer) in enumerate(FAQ, start=1):
        qcol = f"faq_{idx}_question"
        acol = f"faq_{idx}_answer"
        if qcol in fieldnames:
            row[qcol] = question
        if acol in fieldnames:
            row[acol] = answer

    return row


def main() -> int:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    updated = False
    for i, row in enumerate(rows):
        if (row.get("slug") or "").strip() != SLUG:
            continue
        assert topic_from_row(row) == TOPIC or True
        rows[i] = patch_row(row, list(fieldnames))
        updated = True
        break
    if not updated:
        print(f"slug not found: {SLUG}", file=sys.stderr)
        return 1
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Patched {SLUG} in {CSV_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
