#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用語・過去問・まとめ記事・検索意図ガイドの相互リンク用データとヘルパー。"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from question_slug_lib import relative_url_path_past

REPO_ROOT = Path(__file__).resolve().parent.parent
GLOSSARY_SLUGS_JSON = REPO_ROOT / "docs" / "glossary-article-slugs.json"
GLOSSARY_CHECKLIST_CSV = REPO_ROOT / "docs" / "glossary-terms-checklist.csv"
TERM_QUESTION_LINKS_JSON = REPO_ROOT / "docs" / "term-question-links.json"

FIELD_MATOME = {
    "law": ("/articles/kankei-horei-matome.html", "関係法令まとめ（数値・頻度・保存期間）"),
    "rights": ("/articles/rodo-eisei-matome.html", "労働衛生まとめ（測定・管理区分）"),
    "limit": ("/articles/rodo-seiri-matome.html", "労働生理まとめ（体温・循環・音響）"),
}

CATEGORY_MATOME = {
    "関係法令": FIELD_MATOME["law"],
    "労働衛生": FIELD_MATOME["rights"],
    "労働生理": FIELD_MATOME["limit"],
}

# 科目別の検索意図ガイド（試験・学習の入口記事）
# GSC 等で見える表記ゆれ → (用語解説の表示名, slug)。最長一致は呼び出し側で行う。
GLOSSARY_QUERY_ALIASES: list[tuple[str, str, str]] = [
    ("はくろう病", "白ろう", "hakurou"),
    ("白ろう病", "白ろう", "hakurou"),
    ("温熱条件", "WBGT", "wbgt"),
    ("二酸化炭素濃度基準", "労働衛生基準", "rodo-eisei-kijun"),
    ("二酸化炭素濃度", "労働衛生基準", "rodo-eisei-kijun"),
    ("衛生管理者 専任とは", "専任の衛生管理者", "sennin-eisei-kanrisha"),
    ("衛生管理者専任とは", "専任の衛生管理者", "sennin-eisei-kanrisha"),
    ("衛生管理者 専任", "専任の衛生管理者", "sennin-eisei-kanrisha"),
]

INTENT_BY_CATEGORY = {
    "関係法令": [
        ("/articles/dokugaku-guide.html", "独学合格ガイド"),
        ("/articles/nankaisei.html", "合格ライン（何問正解）"),
        ("/articles/shiken-nittei.html", "試験日程・申込"),
        ("/articles/kakomon-nannennbun.html", "過去問は何年分"),
    ],
    "労働衛生": [
        ("/articles/dokugaku-guide.html", "独学合格ガイド"),
        ("/articles/sagyo-kankyo-sokutei-hindo.html", "作業環境測定の頻度"),
        ("/articles/risk-assessment-tejun.html", "リスクアセスメントの手順"),
    ],
    "労働生理": [
        ("/articles/dokugaku-guide.html", "独学合格ガイド"),
        ("/articles/necchuysho-shoudo.html", "熱中症の重症度"),
        ("/articles/benkyou-jikan.html", "勉強時間の目安"),
    ],
}

INTENT_BY_FIELD = {
    "law": INTENT_BY_CATEGORY["関係法令"],
    "rights": INTENT_BY_CATEGORY["労働衛生"],
    "limit": INTENT_BY_CATEGORY["労働生理"],
}

# まとめ記事ページ用：代表用語（スラッグ）
MATOME_FEATURED_TERMS = {
    "kankei-horei-matome.html": [
        "eisei-kanrisha",
        "dai1shu-eisei-kanrisha",
        "dai2shu-eisei-kanrisha",
        "teiki-kenko-shindan",
        "anzen-eisei-kyoiku",
        "rodo-anzen-eisei-ho",
    ],
    "rodo-eisei-matome.html": [
        "sagyo-kankyo-sokutei",
        "kyoyo-nodo",
        "kyokuho-haikisochi",
        "kojin-hogo-gu",
        "risk-assessment",
        "wbgt",
    ],
    "rodo-seiri-matome.html": [
        "necchuysho",
        "taion-chosetsu",
        "junka",
        "soonnsei-nacho",
        "metabolic-rate",
    ],
}

# まとめ記事 → 過去問一覧（科目フィルタの目安テキスト付き）
MATOME_PAST_HUB = "/q/index.html"


def load_glossary_slugs() -> dict[str, str]:
    data = json.loads(GLOSSARY_SLUGS_JSON.read_text(encoding="utf-8"))
    return {str(k): str(v) for k, v in data.items()}


def load_slug_categories() -> dict[str, str]:
    """用語スラッグ → カテゴリ（関係法令 / 労働衛生 / 労働生理）"""
    out: dict[str, str] = {}
    slugs = load_glossary_slugs()
    name_to_slug = slugs
    if not GLOSSARY_CHECKLIST_CSV.is_file():
        return out
    with GLOSSARY_CHECKLIST_CSV.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cat = (row.get("カテゴリ") or "").strip()
            term = (row.get("用語") or "").strip()
            if not cat or not term:
                continue
            slug = name_to_slug.get(term)
            if slug:
                out[slug] = cat
    return out


def load_term_question_links() -> dict[str, list[dict]]:
    if not TERM_QUESTION_LINKS_JSON.is_file():
        return {}
    raw = json.loads(TERM_QUESTION_LINKS_JSON.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    out: dict[str, list[dict]] = {}
    for slug, items in raw.items():
        if isinstance(items, list):
            out[str(slug)] = [x for x in items if isinstance(x, dict)]
    return out


def _term_aliases(name: str) -> list[str]:
    """用語名と括弧内を除いた短い表記など、マッチ用の別名。"""
    aliases = [name]
    short = re.sub(r"（[^）]*）", "", name).strip()
    if short and short not in aliases:
        aliases.append(short)
    short2 = re.sub(r"\([^)]*\)", "", name).strip()
    if short2 and short2 not in aliases:
        aliases.append(short2)
    if "／" in name:
        for part in name.split("／"):
            part = part.strip()
            if part and part not in aliases:
                aliases.append(part)
    return aliases


def glossary_match_entries(text: str, max_terms: int = 5) -> list[tuple[str, str]]:
    """本文から用語名を最長一致で検出し (表示名, slug) のリストを返す。"""
    slugs = load_glossary_slugs()
    names = sorted(slugs.keys(), key=len, reverse=True)
    found: list[tuple[str, str]] = []
    used_slug: set[str] = set()

    for phrase, display, slug in sorted(
        GLOSSARY_QUERY_ALIASES, key=lambda x: len(x[0]), reverse=True
    ):
        if slug in used_slug or phrase not in text:
            continue
        used_slug.add(slug)
        found.append((display, slug))
        if len(found) >= max_terms:
            return found

    for name in names:
        slug = slugs[name]
        if slug in used_slug:
            continue
        if not any(alias in text for alias in _term_aliases(name)):
            continue
        used_slug.add(slug)
        found.append((name, slug))
        if len(found) >= max_terms:
            break
    return found


def question_id_to_web_path(qid: str) -> str | None:
    """past.r06.apr.law.01 → /q/past/r06/apr/law/01/"""
    parts = qid.split(".")
    if len(parts) != 5 or parts[0] != "past":
        return None
    _, era, session, field, num = parts
    rel = relative_url_path_past(era, session, field, num)
    web = "/" + rel.replace("/index.html", "/").replace("\\", "/")
    return web


def question_links_for_term(slug: str, frontmatter_value) -> list[tuple[str, str]]:
    """(href, label) の過去問リンク。frontmatter の related_questions を優先。"""
    links: list[tuple[str, str]] = []
    if frontmatter_value:
        rows = (
            frontmatter_value
            if isinstance(frontmatter_value, (list, tuple))
            else str(frontmatter_value).split(";")
        )
        for row in rows:
            row = str(row).strip()
            if not row:
                continue
            qid, sep, label = row.partition(":")
            qid = qid.strip()
            label = label.strip() if sep else qid
            path = question_id_to_web_path(qid)
            if path:
                links.append((path, label or qid))
        if links:
            return links[:5]

    stored = load_term_question_links().get(slug, [])
    for item in stored[:5]:
        qid = str(item.get("id", "")).strip()
        label = str(item.get("label", qid)).strip()
        path = question_id_to_web_path(qid)
        if path:
            links.append((path, label))
    return links


def matome_for_category(category: str) -> tuple[str, str]:
    return CATEGORY_MATOME.get(category, ("/articles/shiken-kamoku.html", "試験科目と出題範囲"))


def matome_for_field(field: str) -> tuple[str, str]:
    return FIELD_MATOME.get(field, ("/q/index.html", "過去問一覧"))


def intent_links_for_category(category: str, limit: int = 3) -> list[tuple[str, str]]:
    return list(INTENT_BY_CATEGORY.get(category, INTENT_BY_CATEGORY["関係法令"])[:limit])


def intent_links_for_field(field: str, limit: int = 2) -> list[tuple[str, str]]:
    return list(INTENT_BY_FIELD.get(field, INTENT_BY_FIELD["law"])[:limit])


def term_href(slug: str) -> str:
    return f"/terms/{slug}.html"


def slug_display_name(slug: str) -> str:
    slugs = load_glossary_slugs()
    for name, s in slugs.items():
        if s == slug:
            return name
    return slug.replace("-", " ")
