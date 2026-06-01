#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""安全衛生技術センター（*-center ガイド）向けの公式会場案内 URL。"""

from __future__ import annotations

JISSH_TOP = ("安全衛生技術試験協会（公式）", "https://www.jissh.or.jp/")
EXAM_PORTAL = ("安全衛生技術試験協会 試験案内（公式）", "https://www.exam.or.jp/")

# slug -> (リンクラベル, センター公式ページ URL)
CENTER_PAGES: dict[str, tuple[str, str]] = {
    "hokkaido-center": ("北海道安全衛生技術センター（公式・会場案内）", "https://www.exam.or.jp/center_hokkaido/"),
    "tohoku-center": ("東北安全衛生技術センター（公式・会場案内）", "https://www.exam.or.jp/center_tohoku/"),
    "kanto-center": ("関東安全衛生技術センター（公式・会場案内）", "https://www.exam.or.jp/center_kanto/"),
    "chubu-center": ("中部安全衛生技術センター（公式・会場案内）", "https://www.exam.or.jp/center_chubu/"),
    "kinki-center": ("近畿安全衛生技術センター（公式・会場案内）", "https://www.exam.or.jp/center_kinki/"),
    "chushikoku-center": ("中国四国安全衛生技術センター（公式・会場案内）", "https://www.exam.or.jp/center_chushi/"),
    "kyushu-center": ("九州安全衛生技術センター（公式・会場案内）", "https://www.exam.or.jp/center_kyushu/"),
}

CENTER_REGION: dict[str, str] = {
    "hokkaido-center": "北海道",
    "tohoku-center": "東北",
    "kanto-center": "関東",
    "chubu-center": "中部",
    "kinki-center": "近畿",
    "chushikoku-center": "中国・四国",
    "kyushu-center": "九州",
}


def is_exam_center_slug(slug: str) -> bool:
    return slug.endswith("-center") and slug in CENTER_PAGES


def venue_page_for_slug(slug: str) -> tuple[str, str] | None:
    return CENTER_PAGES.get(slug)


def region_for_slug(slug: str) -> str:
    return CENTER_REGION.get(slug, "該当地域")


def md_link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def primary_sources_for_venue(slug: str) -> str:
    parts = [f"{JISSH_TOP[0]}|{JISSH_TOP[1]}", f"{EXAM_PORTAL[0]}|{EXAM_PORTAL[1]}"]
    page = venue_page_for_slug(slug)
    if page:
        parts.append(f"{page[0]}|{page[1]}")
    return ";".join(parts)
