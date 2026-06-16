#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch6: self-study-start へ初学者セット·テキスト比較記事導線。"""

from __future__ import annotations

_AFF_BEGINNER_SET = (
    "affiliate-beginner-material-set:"
    "第二種衛生管理者の初学者向け教材セット3選【テキスト・要点・演習2026】"
)
_AFF_TEXTBOOKS = (
    "affiliate-textbooks-recommend:"
    "第二種衛生管理者のおすすめ参考書・テキスト3選【2026年度版・独学】"
)

_BODY_BEGINNER_SET = (
    "初学者の第1冊は、"
    "affiliate-beginner-material-set でスッキリ·集中レッスン·ユーキャン過去問の3冊を"
    "学習フェーズ別に比較してから固定すると、テキスト→演習の段階投入がぶれにくくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "self-study-start": {
        "related_links_append": [_AFF_BEGINNER_SET, _AFF_TEXTBOOKS],
        "section_body_sentences": {
            "section_3_body": _BODY_BEGINNER_SET,
        },
    },
}
