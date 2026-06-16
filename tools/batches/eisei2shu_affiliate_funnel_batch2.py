#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch2: problem-book-selection へ問題集·テキスト比較記事導線。"""

from __future__ import annotations

_AFF_TEXTBOOKS = (
    "affiliate-textbooks-recommend:"
    "第二種衛生管理者のおすすめ参考書・テキスト3選【2026年度版・独学】"
)
_AFF_PROBLEMS = (
    "affiliate-problem-books:"
    "第二種衛生管理者のおすすめ問題集3選【過去問・予想模試2026】"
)

_BODY_PROBLEMS = (
    "テキスト第1周後の演習1冊は、"
    "affiliate-problem-books でユーキャン·成美堂·労基団連の3冊から選ぶと、"
    "30問本番形式の演習量を確保しやすくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "problem-book-selection": {
        "related_links_append": [_AFF_PROBLEMS, _AFF_TEXTBOOKS],
        "section_body_sentences": {
            "section_3_body": _BODY_PROBLEMS,
        },
    },
}
