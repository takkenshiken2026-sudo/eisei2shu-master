#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch12: past-question-strategy へ模試比較記事導線（問題集は既存）。"""

from __future__ import annotations

_AFF_MOCK = (
    "affiliate-mock-exam-materials:"
    "第二種衛生管理者試験の模試・予想問題3選【30問本番形式2026】"
)

_BODY_MOCK = (
    "本番形式の模試1冊は、"
    "affiliate-mock-exam-materials でユーキャン予想模試·成美堂過去6回·労基団連問題集の3冊を比較してから固定すると、"
    "13:30開始·30問·180分の演習回数が整理しやすくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "past-question-strategy": {
        "related_links_append": [_AFF_MOCK],
        "section_body_sentences": {
            "section_1_body": _BODY_MOCK,
        },
    },
}
