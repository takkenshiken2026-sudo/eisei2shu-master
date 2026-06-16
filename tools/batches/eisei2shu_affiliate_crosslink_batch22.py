#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""二衛 フェーズF batch22: 比較記事5本へ本文相互リンク（bare slug → short link 変換前）。"""

from __future__ import annotations

FUNNEL_PATCHES: dict[str, dict] = {
    "affiliate-textbooks-recommend": {
        "section_body_sentences": {
            "section_4_body": (
                "テキスト第1周後の演習1冊は、"
                "affiliate-problem-books でユーキャン·成美堂·労基団連の3冊を比較してから固定すると、"
                "30問本番形式への移行が進めやすくなります。"
            ),
        },
    },
    "affiliate-correspondence-course": {
        "section_body_sentences": {
            "section_2_body": (
                "月額オンラインを併用する場合は、"
                "affiliate-online-course-compare でSMART合格講座とオンスクを先に比較してから"
                "通信1社へ絞ると二重支出を防げます。"
            ),
        },
    },
    "affiliate-cram-school": {
        "section_body_sentences": {
            "section_5_body": (
                "長期の週次学習が難しい場合は、"
                "affiliate-correspondence-course でLEC第2種通信WebとSMART合格講座を比較し、"
                "通学の代替として1社へ絞る流れが定番です。"
            ),
        },
    },
    "affiliate-retake-short-course": {
        "section_body_sentences": {
            "section_7_body": (
                "全面インプットが必要なら、"
                "affiliate-correspondence-course で通信講座2社を比較してから短期講座と役割分担すると、"
                "再受験の週次演習が整理しやすくなります。"
            ),
        },
    },
    "affiliate-qualification-support-service": {
        "section_body_sentences": {
            "section_7_body": (
                "申込と並行して教材予算を整理する場合は、"
                "affiliate-free-vs-paid-study で無料枠と有料最小セットを先に固定すると、"
                "支援料·講座料との総額比較がぶれにくくなります。"
            ),
        },
    },
}
