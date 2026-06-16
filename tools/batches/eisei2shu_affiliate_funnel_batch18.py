#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch18: final-mock-last-run へ模試·問題集比較記事導線。"""

from __future__ import annotations

_AFF_MOCK = (
    "affiliate-mock-exam-materials:"
    "第二種衛生管理者試験の模試・予想問題3選【30問本番形式2026】"
)
_AFF_PROBLEMS = (
    "affiliate-problem-books:"
    "第二種衛生管理者のおすすめ問題集3選【過去問・予想模試2026】"
)

_BODY_MOCK = (
    "直前模試の問題セットを決める前は、"
    "affiliate-mock-exam-materials でユーキャン予想模試·成美堂過去6回·労基団連問題集の3冊を比較してから"
    "10/4（日）13:30の30問演習に1冊を固定すると、"
    "本番4〜7日前の最終判定が整理しやすくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "final-mock-last-run": {
        "related_links_append": [_AFF_MOCK, _AFF_PROBLEMS],
        "section_body_sentences": {
            "section_1_body": _BODY_MOCK,
        },
    },
}
