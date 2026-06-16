#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch16: self-study-schedule へテキスト·オンライン講座比較記事導線。"""

from __future__ import annotations

_AFF_TEXTBOOKS = (
    "affiliate-textbooks-recommend:"
    "第二種衛生管理者のおすすめ参考書・テキスト3選【2026年度版・独学】"
)
_AFF_ONLINE = (
    "affiliate-online-course-compare:"
    "第二種衛生管理者のオンライン講座比較【SMART合格講座 vs オンスク】独学との併用【2026年度版】"
)

_BODY_TEXTBOOKS = (
    "曜日固定の週間表を書く前に、"
    "affiliate-textbooks-recommend でスッキリ·合格教本·村中テキストの3冊を比較してから"
    "火曜のテキスト枠に1冊を固定すると、"
    "30問·3科目の演習スケジュールに組み込みやすくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "self-study-schedule": {
        "related_links_append": [_AFF_TEXTBOOKS, _AFF_ONLINE],
        "section_body_sentences": {
            "section_1_body": _BODY_TEXTBOOKS,
        },
    },
}
