#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch14: self-study-without-school へ無料有料·オンライン講座比較記事導線。"""

from __future__ import annotations

_AFF_FREE_PAID = (
    "affiliate-free-vs-paid-study:"
    "第二種衛生管理者試験の無料と有料教材の使い分け【独学2026】"
)
_AFF_ONLINE = (
    "affiliate-online-course-compare:"
    "第二種衛生管理者のオンライン講座比較【SMART合格講座 vs オンスク】独学との併用【2026年度版】"
)

_BODY_FREE_PAID = (
    "学校なし独学の教材費を決める前は、"
    "affiliate-free-vs-paid-study で要項·210問·657問一問一答の無料枠と"
    "テキスト1冊+問題集1冊の有料最小セットを先に整理すると、"
    "月額講座との費用比較がぶれにくくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "self-study-without-school": {
        "related_links_append": [_AFF_FREE_PAID, _AFF_ONLINE],
        "section_body_sentences": {
            "section_3_body": _BODY_FREE_PAID,
        },
    },
}
