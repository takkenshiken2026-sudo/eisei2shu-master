#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch7: dokugaku-guide へ無料有料比較記事導線（テキストは既存）。"""

from __future__ import annotations

_AFF_FREE_PAID = (
    "affiliate-free-vs-paid-study:"
    "第二種衛生管理者試験の無料と有料教材の使い分け【独学2026】"
)

_BODY_FREE_PAID = (
    "独学の教材投資を決める前は、"
    "affiliate-free-vs-paid-study で要項·210問·657問一問一答の無料枠と"
    "テキスト1冊+問題集1冊の有料最小セットを先に整理すると、"
    "通信講座との費用比較もぶれにくくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "dokugaku-guide": {
        "related_links_append": [_AFF_FREE_PAID],
        "section_body_sentences": {
            "section_1_body": _BODY_FREE_PAID,
        },
    },
}
