#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch4: tsushin-kouza-vs-dokugaku へ通信講座·無料有料比較記事導線。"""

from __future__ import annotations

_AFF_CORRESPONDENCE = (
    "affiliate-correspondence-course:"
    "第二種衛生管理者試験の通信講座比較【LEC vs SMART】独学との併用【2026年度版】"
)
_AFF_FREE_PAID = (
    "affiliate-free-vs-paid-study:"
    "第二種衛生管理者試験の無料と有料教材の使い分け【独学2026】"
)

_BODY_CORRESPONDENCE = (
    "通信講座を検討する段階では、"
    "affiliate-correspondence-course でLEC第2種通信WebとSMART合格講座の演習量·費用·期間を比較し、"
    "本サイト210問演習は維持したまま8月申込前に1社へ絞ると二重支出を防げます。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "tsushin-kouza-vs-dokugaku": {
        "related_links_append": [_AFF_CORRESPONDENCE, _AFF_FREE_PAID],
        "section_body_sentences": {
            "section_3_body": _BODY_CORRESPONDENCE,
        },
    },
}
