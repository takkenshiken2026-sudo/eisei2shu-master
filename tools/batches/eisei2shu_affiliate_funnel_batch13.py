#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch13: study-plan-working へオンライン·通信講座比較記事導線（テキストは既存）。"""

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
    "繁忙週で週2時間に落ちた社会人は、"
    "affiliate-online-course-compare でSMART合格講座とオンスクを比較し、"
    "通勤枠で視聴できる講座案内を8月申込前に1社へ絞ると、"
    "日曜13:30の30問模試を週次で維持しやすくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "study-plan-working": {
        "related_links_append": [_AFF_ONLINE, _AFF_CORRESPONDENCE],
        "section_body_sentences": {
            "section_2_body": _BODY_ONLINE,
        },
    },
}
