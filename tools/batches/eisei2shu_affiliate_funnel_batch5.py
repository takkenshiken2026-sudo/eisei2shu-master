#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch5: free-materials-online へ無料有料·初学者セット比較記事導線。"""

from __future__ import annotations

_AFF_FREE_PAID = (
    "affiliate-free-vs-paid-study:"
    "第二種衛生管理者試験の無料と有料教材の使い分け【独学2026】"
)
_AFF_BEGINNER_SET = (
    "affiliate-beginner-material-set:"
    "第二種衛生管理者の初学者向け教材セット3選【テキスト・要点・演習2026】"
)

_BODY_FREE_PAID = (
    "有料教材の追加を検討する段階では、"
    "affiliate-free-vs-paid-study で要項·210問·657問一問一答の無料枠と"
    "テキスト1冊+問題集1冊の有料最小セットを先に整理すると、"
    "無料中心の学習計画がぶれにくくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "free-materials-online": {
        "related_links_append": [_AFF_FREE_PAID, _AFF_BEGINNER_SET],
        "section_body_sentences": {
            "section_4_body": _BODY_FREE_PAID,
        },
    },
}
