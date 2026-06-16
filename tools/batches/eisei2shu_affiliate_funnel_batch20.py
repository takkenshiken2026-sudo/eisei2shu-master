#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch20: self-study-mistakes へ問題集·テキスト比較記事導線。"""

from __future__ import annotations

_AFF_PROBLEMS = (
    "affiliate-problem-books:"
    "第二種衛生管理者のおすすめ問題集3選【過去問・予想模試2026】"
)
_AFF_TEXTBOOKS = (
    "affiliate-textbooks-recommend:"
    "第二種衛生管理者のおすすめ参考書・テキスト3選【2026年度版・独学】"
)

_BODY_PROBLEMS = (
    "テキスト読み過ぎで演習が遅れている場合は、"
    "affiliate-problem-books でユーキャン·成美堂·労基団連の3冊から30問向け1冊を選び、"
    "科目別10問/週の枠に先に固定すると、"
    "得点化のタイミングを取り戻しやすくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "self-study-mistakes": {
        "related_links_append": [_AFF_PROBLEMS, _AFF_TEXTBOOKS],
        "section_body_sentences": {
            "section_3_body": _BODY_PROBLEMS,
        },
    },
}
