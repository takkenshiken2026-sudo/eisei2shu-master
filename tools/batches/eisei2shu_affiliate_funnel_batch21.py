#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch21: timed-practice へ問題集比較記事導線（模試は既存）。"""

from __future__ import annotations

_AFF_PROBLEMS = (
    "affiliate-problem-books:"
    "第二種衛生管理者のおすすめ問題集3選【過去問・予想模試2026】"
)

_BODY_PROBLEMS = (
    "段階2の科目別10問·60分演習に使う問題集1冊は、"
    "affiliate-problem-books でユーキャン·成美堂·労基団連の3冊から選び、"
    "タイマー記録表とセットで固定すると、"
    "40点確認の演習量が安定しやすくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "timed-practice": {
        "related_links_append": [_AFF_PROBLEMS],
        "section_body_sentences": {
            "section_1_body": _BODY_PROBLEMS,
        },
    },
}
