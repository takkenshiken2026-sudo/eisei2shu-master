#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズE batch17: simulation-exam-schedule へ模試·問題集比較記事導線。"""

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
    "模試4回の日程をカレンダーに書く前は、"
    "affiliate-mock-exam-materials でユーキャン予想模試·成美堂過去6回·労基団連問題集の3冊を比較してから1冊を固定すると、"
    "7/13·8/17·9/14·10/4の13:30開始·30問演習が整理しやすくなります。"
)

FUNNEL_PATCHES: dict[str, dict] = {
    "simulation-exam-schedule": {
        "related_links_append": [_AFF_MOCK, _AFF_PROBLEMS],
        "section_body_sentences": {
            "section_1_body": _BODY_MOCK,
        },
    },
}
