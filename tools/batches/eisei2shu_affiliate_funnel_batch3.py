#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch3: correspondence-course-guide へ通信·オンライン講座比較記事導線。"""

from __future__ import annotations

_AFF_CORRESPONDENCE = (
    "affiliate-correspondence-course:"
    "第二種衛生管理者試験の通信講座比較【LEC vs SMART】独学との併用【2026年度版】"
)
_AFF_ONLINE = (
    "affiliate-online-course-compare:"
    "第二種衛生管理者のオンライン講座比較【SMART合格講座 vs オンスク】独学との併用【2026年度版】"
)

_BODY_CORRESPONDENCE = (
    "通信講座を1社に絞る前は、"
    "affiliate-correspondence-course でLEC第2種通信WebとSMART合格講座を比較し、"
    "30問演習量は210問で維持したまま8月申込前に決めると二重支出を防げます。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "correspondence-course-guide": {
        "related_links_append": [_AFF_CORRESPONDENCE, _AFF_ONLINE],
        "section_body_sentences": {
            "section_2_body": _BODY_CORRESPONDENCE,
        },
    },
}
