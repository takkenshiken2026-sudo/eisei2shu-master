#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""articles/index.html の記事カード一覧をカテゴリ別に再生成する。"""

from __future__ import annotations

import html
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO / "articles"
INDEX_FILE = ARTICLES_DIR / "index.html"

CATEGORIES = [
    ("hub", "まとめ・索引", "hub"),
    ("exam", "受験・合格", "exam"),
    ("study", "勉強法・教材", "study"),
    ("law", "関係法令", "law"),
    ("rights", "労働衛生", "rights"),
    ("limit", "労働生理", "limit"),
    ("venue", "試験会場・地域", "venue"),
    ("other", "その他", "other"),
]

CAT_LABEL = {c[0]: c[1] for c in CATEGORIES}
CAT_MOD = {c[0]: c[2] for c in CATEGORIES}


def extract_title(text: str) -> str:
    m = re.search(r'<h1 class="article-title">([^<]+)</h1>', text)
    if m:
        return html.unescape(m.group(1).strip())
    m = re.search(r"<title>([^<|｜]+)", text)
    if m:
        return html.unescape(m.group(1).strip())
    return ""


def short_title(title: str) -> str:
    t = re.split(r"[【|｜]", title, maxsplit=1)[0].strip()
    return t or title


def categorize(slug: str, title: str) -> str:
    s = slug.lower()
    t = title

    if s in {"about"} or "matome" in s or s.startswith("category-"):
        return "hub"
    if s.endswith("-center"):
        return "venue"

    if any(
        k in s
        for k in (
            "3kagetsu", "6kagetsu", "bookmark", "ichimon", "saijuken",
        )
    ):
        return "study"
    if any(
        k in s
        for k in (
            "shiken", "juken", "goukaku", "menkyo", "nankai", "kamoku",
            "shikaku-merit", "tsugi-toru", "jisshi-moshikomi", "shutsudai",
        )
    ):
        return "exam"
    if any(
        k in s
        for k in (
            "dokugaku", "benkyou", "textbook", "kakomon", "osusume-app",
            "tsushin", "suuchi-anki", "ikkagetsu", "jikan-haibun",
            "kanri-kubun", "niji-kenko", "sagyo-shunin",
        )
    ):
        return "study"
    if any(
        k in s
        for k in (
            "necchuysho", "soonssei", "soonnsei", "ichisanka-tanso",
            "shindo-hakuro",
        )
    ):
        return "limit"
    if any(
        k in s
        for k in (
            "wbgt", "hoshu-bunseki", "kyokuho", "risk-assessment", "hogo-gu",
            "kagaku-busshitsu", "karotein", "hoshasen", "denri-hoshasen",
            "sekimen", "sagyo-kankyo",
        )
    ):
        return "rights"
    if any(
        k in s
        for k in (
            "eisei", "jinpai", "anzen", "kenko", "stress", "sanso", "yuki",
            "tokubetsu-kyoiku", "choujikan", "sennin", "kanri-taisei", "sangyo-i",
            "dai2shu", "1shu-2shu", "kiroku-hozon",
        )
    ):
        return "law"

    if "労働生理" in t or "熱中症" in t or "騒音" in t:
        return "limit"
    if "労働衛生" in t or "WBGT" in t or "作業環境" in t:
        return "rights"
    if "関係法令" in t or "衛生管理者" in t or "じん肺" in t:
        return "law"
    if "受験" in t or "合格" in t or "試験日程" in t:
        return "exam"
    if "独学" in t or "テキスト" in t or "勉強" in t:
        return "study"
    return "other"


def collect_articles() -> list[dict]:
    items: list[dict] = []
    for path in sorted(ARTICLES_DIR.glob("*.html")):
        if path.name == "index.html":
            continue
        text = path.read_text(encoding="utf-8")
        title = extract_title(text)
        if not title:
            continue
        slug = path.stem
        items.append(
            {
                "slug": slug,
                "href": f"/articles/{slug}.html",
                "title": title,
                "short": short_title(title),
                "cat": categorize(slug, title),
            }
        )
    return items


def render_card(item: dict) -> str:
    cat = item["cat"]
    mod = CAT_MOD[cat]
    label = CAT_LABEL[cat]
    return f"""    <li class="idx-card-wrap" data-cat="{mod}">
      <a href="{html.escape(item['href'])}" class="idx-card idx-card--{mod}">
        <span class="idx-card-badge">{html.escape(label)}</span>
        <span class="idx-card-title">{html.escape(item['short'])}</span>
        <span class="idx-card-full">{html.escape(item['title'])}</span>
      </a>
    </li>"""


def render_index_body(items: list[dict]) -> str:
    by_cat: dict[str, list[dict]] = {c[0]: [] for c in CATEGORIES}
    for item in items:
        by_cat.setdefault(item["cat"], []).append(item)
    for cat_items in by_cat.values():
        cat_items.sort(key=lambda x: x["short"])

    sections: list[str] = []
    for cat_id, _label, mod in [(c[0], c[1], c[2]) for c in CATEGORIES]:
        cat_items = by_cat.get(cat_id, [])
        if not cat_items:
            continue
        cards = "\n".join(render_card(i) for i in cat_items)
        sections.append(
            f"""  <section class="idx-cat-section idx-cat-section--{mod}" data-cat="{mod}" aria-labelledby="idx-cat-{mod}">
    <div class="idx-cat-head">
      <h2 id="idx-cat-{mod}" class="idx-cat-title">{html.escape(CAT_LABEL[cat_id])}</h2>
      <span class="idx-cat-count">{len(cat_items)}本</span>
    </div>
    <ul class="idx-card-grid">
{cards}
    </ul>
  </section>"""
        )

    nav_btns = "\n".join(
        f'    <button type="button" class="idx-filter-btn" data-filter="{c[0]}">{html.escape(c[1])}</button>'
        for c in CATEGORIES
        if by_cat.get(c[0])
    )

    body = f"""  <nav class="idx-filters" aria-label="カテゴリで絞り込み">
    <button type="button" class="idx-filter-btn is-active" data-filter="all">すべて</button>
{nav_btns}
  </nav>

  <div id="article-index-sections" class="idx-sections">
{chr(10).join(sections)}
  </div>"""
    return body


def patch_index(items: list[dict]) -> None:
    text = INDEX_FILE.read_text(encoding="utf-8")
    body = render_index_body(items)
    # idx-count から footer 直前の旧一覧まで置換
    pattern = re.compile(
        r'  <p class="idx-count">.*?'
        r'<div id="article-index-sections" class="idx-sections">.*?</div>\s*\n\n'
        r'<footer class="site-footer">',
        re.DOTALL,
    )
    replacement = (
        f'  <p class="idx-count">全 {len(items)} 本（静的HTML）</p>\n\n'
        f"{body}\n\n<footer class=\"site-footer\">"
    )
    new_text, n = pattern.subn(replacement, text, count=1)
    if n != 1:
        raise RuntimeError("articles/index.html の置換箇所が見つかりません")
    INDEX_FILE.write_text(new_text, encoding="utf-8")


def main() -> None:
    items = collect_articles()
    patch_index(items)
    print(f"更新: {INDEX_FILE}（{len(items)} 記事）")


if __name__ == "__main__":
    main()
