#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二種衛生管理者 試験日検索ページの文言・FAQ。"""

from __future__ import annotations

PAGE_SLUG = "exam-dates"
PAGE_TITLE = "第二種衛生管理者試験の試験日一覧（会場別・検索）"
PAGE_LEAD = (
    "安全衛生技術試験協会の公開日程を会場別に検索できます。"
    "本日以降の試験日のみ表示しています。"
)
META_DESCRIPTION = (
    "第二種衛生管理者試験の試験日を会場別に検索。"
    "北海道〜九州の各センター・東京・大阪試験場の一覧とカレンダー表。"
    "最新情報は安全衛生技術試験協会公式で確認。"
)
OFFICIAL_SCHEDULE_URL = "https://www.exam.or.jp/schedule/h_nittei502/"
OFFICIAL_APPLICATION_URL = "https://www.exam.or.jp/online/"
APPLICATION_GUIDE_HREF = "../articles/exam-application-flow/"


def faq_items() -> list[tuple[str, str]]:
    return [
        (
            "第二種と第一種の試験日は同じですか？",
            "はい。同日・同会場で実施されます。",
        ),
        (
            "東京試験場と関東センターの違いは？",
            "関東センター（埼玉）と東京試験場では開催日数・日程が異なります。"
            "東京試験場は日数が多い一方、申込が集中しやすいです。",
        ),
        (
            "申込はどこから行いますか？",
            f"協会の<a href=\"{OFFICIAL_APPLICATION_URL}\" target=\"_blank\" rel=\"noopener noreferrer\">オンライン受験申請</a>からです。"
            "受験料8,800円・希望試験日の約2か月前から先着。"
            f"手順は<a href=\"{APPLICATION_GUIDE_HREF}\">申込の流れ</a>も参照してください。",
        ),
    ]
