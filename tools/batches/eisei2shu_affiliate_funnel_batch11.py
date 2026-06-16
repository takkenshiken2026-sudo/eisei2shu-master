#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch11: drill-volume-guide へ問題集·模試比較記事導線。"""

from __future__ import annotations

_AFF_PROBLEMS = (
    "affiliate-problem-books:"
    "第二種衛生管理者のおすすめ問題集3選【過去問・予想模試2026】"
)
_AFF_MOCK = (
    "affiliate-mock-exam-materials:"
    "第二種衛生管理者試験の模試・予想問題3選【30問本番形式2026】"
)

_BODY_PROBLEMS = (
    "テキスト第1周後の演習1冊は、"
    "affiliate-problem-books でユーキャン·成美堂·労基団連の3冊から選ぶと、"
    "30問本番形式の演習量を確保しやすくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "drill-volume-guide": {
        "related_links_append": [_AFF_PROBLEMS, _AFF_MOCK],
        "section_body_sentences": {
            "section_3_body": _BODY_PROBLEMS,
        },
    },
}
