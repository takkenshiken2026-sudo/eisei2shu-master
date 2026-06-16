#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch9: textbook-vs-past-questions へテキスト·問題集比較記事導線。"""

from __future__ import annotations

_AFF_TEXTBOOKS = (
    "affiliate-textbooks-recommend:"
    "第二種衛生管理者のおすすめ参考書・テキスト3選【2026年度版・独学】"
)
_AFF_PROBLEMS = (
    "affiliate-problem-books:"
    "第二種衛生管理者のおすすめ問題集3選【過去問・予想模試2026】"
)

_BODY_TEXTBOOKS = (
    "テキスト1冊は、"
    "affiliate-textbooks-recommend でスッキリ·合格教本·村中テキストの3冊を比較してから固定すると、"
    "骨格1周→科目別10問の優先順位がぶれにくくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "textbook-vs-past-questions": {
        "related_links_append": [_AFF_TEXTBOOKS, _AFF_PROBLEMS],
        "section_body_sentences": {
            "section_2_body": _BODY_TEXTBOOKS,
        },
    },
}
