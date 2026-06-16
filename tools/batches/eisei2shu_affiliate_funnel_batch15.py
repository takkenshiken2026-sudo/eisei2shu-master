#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch15: balance-work-study へオンライン·通信講座比較記事導線。"""

from __future__ import annotations

_AFF_ONLINE = (
    "affiliate-online-course-compare:"
    "第二種衛生管理者のオンライン講座比較【SMART合格講座 vs オンスク】独学との併用【2026年度版】"
)
_AFF_CORRESPONDENCE = (
    "affiliate-correspondence-course:"
    "第二種衛生管理者試験の通信講座比較【LEC vs SMART】独学との併用【2026年度版】"
)

_BODY_ONLINE = (
    "残業週で火木の夜枠が消えた場合は、"
    "affiliate-online-course-compare でSMART合格講座とオンスクを比較し、"
    "通勤30分枠で視聴できる講座案内を先に固定すると、"
    "日曜の30問模試で週5時間の演習予算を維持しやすくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "balance-work-study": {
        "related_links_append": [_AFF_ONLINE, _AFF_CORRESPONDENCE],
        "section_body_sentences": {
            "section_2_body": _BODY_ONLINE,
        },
    },
}
