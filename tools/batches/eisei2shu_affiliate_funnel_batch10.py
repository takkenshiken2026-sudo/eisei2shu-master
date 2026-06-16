#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch10: benkyou-jikan へ無料有料·テキスト比較記事導線。"""

from __future__ import annotations

_AFF_FREE_PAID = (
    "affiliate-free-vs-paid-study:"
    "第二種衛生管理者試験の無料と有料教材の使い分け【独学2026】"
)
_AFF_TEXTBOOKS = (
    "affiliate-textbooks-recommend:"
    "第二種衛生管理者のおすすめ参考書・テキスト3選【2026年度版・独学】"
)

_BODY_FREE_PAID = (
    "総時間60時間前後を試す前に、"
    "affiliate-free-vs-paid-study で要項·210問·657問一問一答の無料枠と"
    "テキスト1冊+問題集1冊の有料最小セットを先に整理すると、"
    "週次計画への教材投資がぶれにくくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "benkyou-jikan": {
        "related_links_append": [_AFF_FREE_PAID, _AFF_TEXTBOOKS],
        "section_body_sentences": {
            "section_1_body": _BODY_FREE_PAID,
        },
    },
}
