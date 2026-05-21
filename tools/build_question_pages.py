#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV から SEO 用の静的問題ページ（docs/question-id-url-slug-spec.md）を生成する。

使用例:
  python3 tools/build_question_pages.py
  python3 tools/build_question_pages.py --base-url https://example.github.io/repo --site-prefix repo

出力:
  - q/past/.../index.html, q/orig/.../index.html
  - q/index.html（過去問一覧：開催回×科目のグリッド）
  - リポジトリ直下の sitemap.xml（トップ・about・privacy・q 配下の全 URL）
  - リポジトリ直下の robots.txt（Sitemap 行を上記に合わせて更新）
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

_TOOLS_DIR = Path(__file__).resolve().parent
ROOT = _TOOLS_DIR.parent
FORM_URL_EISEI2 = "https://forms.gle/51E5d6D41BZETjhY6"
SITE_COPYRIGHT_EISEI2 = "© 2026 二衛マスター"
BRAND_NAME = "二衛マスター"
EXAM_NAME_OFFICIAL = "第二種衛生管理者試験"
SESSION_ORDER = ("cat90", "zenki", "koki", "apr", "oct")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from html_footer import (
    ROBOTS_INDEX_FOLLOW,
    breadcrumb_html,
    site_page_footer,
    site_page_header,
    site_page_wrap_close,
    site_page_wrap_open,
)
from learning_links_lib import matome_for_field
from question_slug_lib import (
    FIELD_MAP,
    era_slug_past,
    month_key_for_pool,
    normalize_era,
    question_string_id_orig,
    question_string_id_past,
    relative_url_path_orig,
    relative_url_path_past,
    session_or_pool_slug,
)
from csv_to_eisei2_master import discover_pool_years, make_id
from render_learning_hub import render_session_hub_page_body

FIELD_LABEL_JA = {"law": "関係法令", "rights": "労働衛生", "limit": "労働生理"}
EXPLANATION_META_CSV = "eisei2_past_explanation_meta.csv"


def load_rows(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    return list(csv.DictReader(text.splitlines()))


def parse_row(row: dict, line_no: int) -> dict:
    科目 = (row.get("科目") or "").strip()
    field = FIELD_MAP.get(科目)
    if not field:
        raise ValueError(f"不明な科目: {科目!r}")

    era_raw = (row.get("開催年数") or "").strip()
    era_n = normalize_era(era_raw)
    is_orig = era_n == "オリジナル"

    month_raw = (row.get("開催月") or "").strip()
    sp = session_or_pool_slug(era_raw, month_raw)

    num = int(str(row.get("問番号") or "").strip())

    opts = [(row.get(f"({i})") or "").strip() for i in range(1, 6)]
    if not all(opts):
        raise ValueError("選択肢欠け")

    raw_ans = str(row.get("正答番号") or "").strip()
    if not raw_ans:
        raise ValueError("正答番号なし")
    ans1 = int(raw_ans)
    if not (1 <= ans1 <= 5):
        raise ValueError(f"正答番号が1〜5以外: {ans1}")

    text_q = (row.get("問") or "").strip()
    if not text_q:
        raise ValueError("問題文なし")

    exp_raw = (row.get("解説") or "").strip()
    exp = exp_raw if exp_raw else f"正解は選択肢{ans1}。解説テキストは CSV で未入力です。"

    if is_orig:
        era_slug = None
        group_key = ("orig", sp, field)
    else:
        era_slug = era_slug_past(era_raw)
        group_key = ("past", era_slug, sp, field)

    return {
        "is_orig": is_orig,
        "era_raw": era_raw,
        "era_n": era_n,
        "month_raw": month_raw,
        "session_or_pool": sp,
        "era_slug": era_slug,
        "field": field,
        "num": num,
        "text": text_q,
        "opts": opts,
        "ans_index0": ans1 - 1,
        "ans_display": str(ans1),
        "exp": exp,
        "group_key": group_key,
        "line_no": line_no,
    }


def compute_widths(rows: list[dict]) -> dict[tuple, int]:
    nums: dict[tuple, list[int]] = defaultdict(list)
    for r in rows:
        nums[r["group_key"]].append(r["num"])
    widths: dict[tuple, int] = {}
    for k, ns in nums.items():
        mx = max(ns)
        widths[k] = 3 if mx >= 100 else 2
    return widths


def format_qwidth(num: int, width: int) -> str:
    return str(num).zfill(width)


def rel_to_root_index(rel_file: Path) -> str:
    """q/past/r07/koki/law/03/index.html → ../../../../../../index.html"""
    depth = len(rel_file.parent.parts)
    if depth == 0:
        return "index.html"
    return "/".join([".."] * depth) + "/index.html"


def rel_to_site_css(rel_file: Path) -> str:
    depth = len(rel_file.parent.parts)
    if depth == 0:
        return "site-pages.css"
    return "/".join([".."] * depth) + "/site-pages.css"


def site_depth_to_root(rel_file: Path) -> int:
    return len(rel_file.parent.parts)


def href_repo_root(rel_file: Path, filename: str) -> str:
    d = site_depth_to_root(rel_file)
    if d == 0:
        return filename
    return "/".join([".."] * d) + "/" + filename


def href_q_index(rel_file: Path) -> str:
    """リポジトリ直下の q/index.html（過去問一覧）への相対パス。"""
    parts_n = len(rel_file.parent.parts)
    if parts_n <= 1:
        return "index.html"
    return "/".join([".."] * (parts_n - 1)) + "/index.html"


def href_session_hub(rel_file: Path) -> str | None:
    """開催回ハブ q/past/{era}/{session}/index.html への相対パス。"""
    parts = rel_file.parent.parts
    if len(parts) < 5 or parts[0] != "q" or parts[1] != "past":
        return None
    up = len(parts) - 4
    if up <= 0:
        return None
    return "/".join([".."] * up) + "/index.html"


def session_hub_canonical(base_url: str, site_prefix: str, era_slug: str, session: str) -> str:
    web_dir = f"q/past/{era_slug}/{session}/"
    return public_url(base_url, site_prefix, web_dir)


def render_static_q_footer(rel_file: Path, *, current_q_index: bool = False) -> str:
    cur = ' aria-current="page"' if current_q_index else ""

    def esc_href(dest: str) -> str:
        return html.escape(href_repo_root(rel_file, dest))

    return f"""<footer class="q-static-footer">
  <nav class="q-static-footer-nav" aria-label="サイトの他ページ">
    <a href="{esc_href("index.html")}">トップ</a>
    <a href="{esc_href("about.html")}">このサイトについて</a>
    <a href="{html.escape(href_q_index(rel_file))}"{cur}>過去問一覧</a>
    <a href="{esc_href("terms/index.html")}">用語集</a>
    <a href="{esc_href("privacy-terms.html")}">プライバシー</a>
    <a href="{html.escape(FORM_URL_EISEI2)}" target="_blank" rel="noopener noreferrer">お問い合わせ</a>
  </nav>
  <p><small>学習用サンプル。出題・法令の最新情報は公式で確認してください。</small></p>
  <p><small>{html.escape(SITE_COPYRIGHT_EISEI2)}</small></p>
</footer>"""


def era_sort_tuple(era_slug: str) -> tuple[int, int]:
    if not era_slug:
        return (99, 0)
    kind = era_slug[0].lower()
    try:
        n = int(era_slug[1:])
    except ValueError:
        return (99, 0)
    if kind == "s":
        return (0, n)
    if kind == "h":
        return (1, n)
    if kind == "r":
        return (2, n)
    return (99, 0)


def session_sort_tuple(session: str) -> tuple[int, str]:
    if session in SESSION_ORDER:
        return (SESSION_ORDER.index(session), session)
    return (len(SESSION_ORDER), session)


def href_past_question_from_q_index(r: dict) -> str:
    rel = Path(
        relative_url_path_past(
            r["era_slug"], r["session_or_pool"], r["field"], r["qwidth"]
        )
    )
    return "/".join(rel.parts[1:])


def build_past_list_sections(parsed_rows: list[dict]) -> str:
    """q/index.html 本文: 開催回ごと・科目別の過去問リンク。"""
    past = [r for r in parsed_rows if not r["is_orig"]]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in past:
        groups[(r["era_slug"], r["session_or_pool"])].append(r)
    sorted_keys = sorted(
        groups.keys(),
        key=lambda k: (era_sort_tuple(k[0]), session_sort_tuple(k[1])),
    )
    sections: list[str] = []
    field_order = ("law", "rights", "limit")
    for era_slug, session in sorted_keys:
        rows = groups[(era_slug, session)]
        sample = rows[0]
        heading = breadcrumb_label_past(sample["era_raw"], sample["month_raw"])
        sid = f"{html.escape(era_slug)}-{html.escape(session)}"
        hub_href = html.escape(f"past/{era_slug}/{session}/index.html")
        subblocks: list[str] = []
        for fk in field_order:
            sub = [r for r in rows if r["field"] == fk]
            if not sub:
                continue
            sub.sort(key=lambda x: x["num"])
            label_ja = FIELD_LABEL_JA[fk]
            lis = "".join(
                f'<li><a href="{html.escape(href_past_question_from_q_index(r))}">第{r["num"]}問</a></li>'
                for r in sub
            )
            subblocks.append(
                f'<section class="q-session-field" aria-labelledby="sf-{sid}-{fk}">'
                f'<h3 id="sf-{sid}-{fk}" class="q-field-subhead">{html.escape(label_ja)}</h3>'
                f'<ol class="q-year-list">{lis}</ol></section>'
            )
        inner = "".join(subblocks)
        sections.append(
            f'<section class="glos-cat-section q-year-section" aria-labelledby="sess-{sid}">'
            f'<h2 id="sess-{sid}" class="glos-cat-heading glos-cat-heading--ja">'
            f'<a href="{hub_href}">{html.escape(heading)}</a>（開催回まとめ）</h2>'
            f"{inner}</section>"
        )
    return "\n".join(sections) if sections else "<p>過去問の静的ページがありません。</p>"


def public_url(base_url: str, site_prefix: str, rel_path: str) -> str:
    """相対パス rel_path（例 q/past/.../ または index.html）→ 絶対URL"""
    base = base_url.rstrip("/")
    pfx = (site_prefix or "").strip("/").strip()
    rel_path = rel_path.lstrip("/")
    if pfx:
        return f"{base}/{pfx}/{rel_path}"
    return f"{base}/{rel_path}"


def meta_description(text: str, limit: int = 155) -> str:
    one = re.sub(r"\s+", " ", text).strip()
    if len(one) <= limit:
        return one
    return one[: limit - 1] + "…"


def breadcrumb_label_past(era_raw: str, month_raw: str) -> str:
    e = (era_raw or "").strip()
    m = (month_raw or "").strip()
    if m:
        return f"{e}・{m}"
    return e


def explanation_meta_key(era_raw: str, month_raw: str, num: int, field: str) -> tuple[str, str, str, str]:
    return (
        (era_raw or "").strip(),
        (month_raw or "").strip(),
        str(num),
        FIELD_LABEL_JA.get(field, field),
    )


def load_explanation_meta(data_dir: Path) -> dict[tuple[str, str, str, str], dict[str, str]]:
    path = data_dir / EXPLANATION_META_CSV
    if not path.is_file():
        return {}
    rows = load_rows(path)
    out: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (
            (row.get("開催年数") or "").strip(),
            (row.get("開催月") or "").strip(),
            (row.get("問番号") or "").strip(),
            (row.get("科目") or "").strip(),
        )
        out[key] = {
            "explanation_summary": (row.get("explanation_summary") or "").strip(),
            "explanation_correct": (row.get("explanation_correct") or "").strip(),
            "explanation_choices": (row.get("explanation_choices") or "").strip(),
            "explanation_point": (row.get("explanation_point") or "").strip(),
        }
    return out


def eisei2_page_and_row(
    r: dict,
    pool_year: dict[tuple[str, str], int],
    *,
    rel_path: Path,
    explanation_meta: dict[tuple[str, str, str, str], dict[str, str]] | None = None,
) -> tuple[dict, dict]:
    """テンプレ build_past_question_pages 用の page / row dict。"""
    field = r["field"]
    field_ja = FIELD_LABEL_JA[field]
    era = normalize_era(r["era_raw"])
    bk = month_key_for_pool({"開催年数": r["era_raw"], "開催月": r["month_raw"]})
    py = pool_year[(era, bk)]
    wareki = breadcrumb_label_past(r["era_raw"], r["month_raw"])
    stem_plain = r["text"]
    stem_html = html.escape(stem_plain).replace("\n", "<br>\n")
    if not stem_html.startswith("<"):
        stem_html = f"<p>{stem_html}</p>"
    ext = r["is_orig"]
    app_id = make_id(py, r["num"], field, ext)
    meta = {}
    if explanation_meta is not None:
        meta = explanation_meta.get(
            explanation_meta_key(r["era_raw"], r["month_raw"], r["num"], field),
            {},
        )
    return (
        {
            "year": py,
            "year_label": wareki if not ext else "オリジナル",
            "qno": r["num"],
            "wareki": wareki,
            "category": field_ja,
            "stem_html": stem_html,
            "stem_plain": stem_plain,
            "opts": r["opts"],
            "correct": int(r["ans_display"]),
            "is_exempt": False,
            "is_invalidated": False,
            "note": "",
            "app_id": app_id,
            "tags": [],
            "rel_path": str(rel_path).replace("\\", "/"),
        },
        {
            "explanation": r["exp"],
            "explanation_summary": meta.get("explanation_summary", ""),
            "explanation_correct": meta.get("explanation_correct", ""),
            "explanation_choices": meta.get("explanation_choices", ""),
            "explanation_point": meta.get("explanation_point", ""),
            "related_links": "",
        },
    )


def build_question_html(
    r: dict,
    rel_path: Path,
    all_pages: list[dict],
    pool_year: dict[tuple[str, str], int],
    glossary_lookup: dict[str, str],
    guides: list[dict[str, str]],
) -> str:
    from build_past_question_pages import (
        HEAD_FONTS,
        build_explanation_html,
        build_related_links_html,
        rel_css,
        rel_href,
        rel_theme_css,
    )

    page, row = eisei2_page_and_row(
        r, pool_year, rel_path=rel_path, explanation_meta=r.get("explanation_meta")
    )
    is_orig = r["is_orig"]
    field_ja = FIELD_LABEL_JA[r["field"]]
    num = r["num"]

    if is_orig:
        title_mid = f"オリジナル・{field_ja} 第{num}問"
        context_line = f"オリジナル · {field_ja}"
        crumb_items: list[tuple[str, str | None]] = [
            ("トップ", "index.html"),
            (title_mid, None),
        ]
    else:
        title_mid = f"{breadcrumb_label_past(r['era_raw'], r['month_raw'])}・{field_ja} 第{num}問"
        context_line = f"{page['wareki']} · {field_ja}"
        crumb_items = [
            ("トップ", "index.html"),
            ("過去問一覧", "q/index.html"),
        ]
        session_label = breadcrumb_label_past(r["era_raw"], r["month_raw"])
        if href_session_hub(rel_path):
            parts = rel_path.parts
            session_rel = "/".join(parts[1:4]) + "/index.html"
            crumb_items.append((session_label, session_rel))
        crumb_items.append((title_mid, None))

    title = f"{title_mid}｜{BRAND_NAME}（{EXAM_NAME_OFFICIAL}）"
    desc = meta_description(r["text"])
    canonical = r["canonical"]
    heading = title_mid

    opts_html = "".join(
        f'<li class="q-opt"><span class="q-opt-num">（{i}）</span> {html.escape(o)}</li>'
        for i, o in enumerate(page["opts"], start=1)
    )
    ans_block = f'<p>正答は <strong>（{page["correct"]}）</strong> です。</p>'
    exp_html = build_explanation_html(page, row)
    related_html = build_related_links_html(
        page, row, rel_path, all_pages, glossary_lookup, guides
    )

    base_url = r["base_url"].rstrip("/")
    site_prefix = r["site_prefix"].strip("/").strip()

    def full_site_url(path_after_root: str) -> str:
        path_after_root = path_after_root.lstrip("/")
        if site_prefix:
            return f"{base_url}/{site_prefix}/{path_after_root}"
        return f"{base_url}/{path_after_root}"

    ld_items: list[dict] = [
        {"@type": "ListItem", "position": 1, "name": "トップ", "item": full_site_url("index.html")},
    ]
    pos = 2
    if not is_orig:
        ld_items.append(
            {
                "@type": "ListItem",
                "position": pos,
                "name": "過去問一覧",
                "item": full_site_url("q/index.html"),
            }
        )
        pos += 1
        if len(crumb_items) >= 4:
            ld_items.append(
                {
                    "@type": "ListItem",
                    "position": pos,
                    "name": crumb_items[2][0],
                    "item": session_hub_canonical(
                        base_url, site_prefix, r["era_slug"], r["session_or_pool"]
                    ),
                }
            )
            pos += 1
    ld_items.append(
        {"@type": "ListItem", "position": pos, "name": title_mid, "item": canonical}
    )

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": canonical + "#webpage",
                "url": canonical,
                "name": title,
                "description": desc,
                "inLanguage": "ja-JP",
            },
            {"@type": "BreadcrumbList", "itemListElement": ld_items},
        ],
    }

    css_href = rel_css(rel_path)
    theme_href = rel_theme_css(rel_path)
    site_header = site_page_header(rel_path, current="q")
    site_breadcrumb = breadcrumb_html(rel_path, crumb_items)
    site_footer = site_page_footer(rel_path, current="q")
    app_href = rel_href(rel_path, f"index.html#past-play-{page['app_id']}")
    app_label = "アプリで演習する" if not is_orig else "アプリでオリジナル問題を開く"
    if is_orig:
        app_href = rel_href(rel_path, "index.html#orig")

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{ROBOTS_INDEX_FOLLOW}
<link rel="canonical" href="{html.escape(canonical)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{html.escape(canonical)}">
<meta name="twitter:card" content="summary">
{HEAD_FONTS}
<link rel="stylesheet" href="{html.escape(css_href)}">
<link rel="stylesheet" href="{html.escape(theme_href)}">
<script type="application/ld+json">
{json.dumps(json_ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
{site_page_wrap_open()}
{site_header}
<main class="q-static-main">
  {site_breadcrumb}
  <p class="q-meta-line">{html.escape(context_line)}</p>
  <h1 class="q-h1">{html.escape(heading)}</h1>
  <p class="q-page-lead">{html.escape(page["stem_plain"])}</p>
  <section class="q-block" aria-labelledby="q-stem-h">
    <h2 id="q-stem-h" class="q-h2">問題</h2>
    <div class="q-stem">{page["stem_html"]}</div>
  </section>
  <section class="q-block" aria-labelledby="q-opts-h">
    <h2 id="q-opts-h" class="q-h2">選択肢</h2>
    <ol class="q-opts">
      {opts_html}
    </ol>
  </section>
  <section class="q-block q-answer" aria-labelledby="q-ans-h">
    <h2 id="q-ans-h" class="q-h2">正答</h2>
    {ans_block}
  </section>
  <section class="q-block" aria-labelledby="q-exp-h">
    <h2 id="q-exp-h" class="q-h2">解説</h2>
    {exp_html}
  </section>
  {related_html}
  <p class="q-app-link"><a href="{html.escape(app_href)}">{html.escape(app_label)}</a></p>
</main>
{site_footer}
{site_page_wrap_close()}
</body>
</html>
"""


def write_session_hubs(
    out_root: Path,
    parsed_rows: list[dict],
    base_url: str,
    site_prefix: str,
    urls_for_sitemap: list[str],
) -> None:
    """開催回ハブ q/past/{era}/{session}/index.html を生成する。"""
    past = [r for r in parsed_rows if not r["is_orig"]]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in past:
        groups[(r["era_slug"], r["session_or_pool"])].append(r)

    field_order = ("law", "rights", "limit")
    for (era_slug, session), rows in sorted(
        groups.items(),
        key=lambda kv: (era_sort_tuple(kv[0][0]), session_sort_tuple(kv[0][1])),
    ):
        sample = rows[0]
        heading = breadcrumb_label_past(sample["era_raw"], sample["month_raw"])
        rel = Path("q") / "past" / era_slug / session / "index.html"
        canonical = session_hub_canonical(base_url, site_prefix, era_slug, session)
        root_idx = href_repo_root(rel, "index.html")
        q_hub_idx = href_q_index(rel)
        css_href = rel_to_site_css(rel)
        meta_desc = (
            f"{EXAM_NAME_OFFICIAL}・{heading}の過去問30問を科目別に一覧。"
            "関係法令・労働衛生・労働生理ごとに解説付きで確認できます。"
        )
        title = f"{heading} 過去問一覧｜{BRAND_NAME}（{EXAM_NAME_OFFICIAL}）"

        subblocks: list[str] = []
        for fk in field_order:
            sub = sorted([r for r in rows if r["field"] == fk], key=lambda x: x["num"])
            if not sub:
                continue
            matome_href, matome_label = matome_for_field(fk)
            label_ja = FIELD_LABEL_JA[fk]
            lis = "".join(
                f'<li><a href="{html.escape(href_past_question_from_hub(era_slug, session, r))}">'
                f'第{r["num"]}問</a></li>'
                for r in sub
            )
            subblocks.append(
                f'<section class="q-session-field" aria-labelledby="hub-{era_slug}-{session}-{fk}">'
                f'<h3 id="hub-{era_slug}-{session}-{fk}" class="q-field-subhead">{html.escape(label_ja)}</h3>'
                f'<p class="q-meta"><a href="{html.escape(href_repo_root(rel, matome_href.lstrip("/")))}">'
                f"{html.escape(matome_label)}</a></p>"
                f'<ol class="q-year-list">{lis}</ol></section>'
            )

        body_main = render_session_hub_page_body(heading, "".join(subblocks))
        hub_item_url = public_url(base_url, site_prefix, "q/index.html")
        json_ld = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "CollectionPage",
                    "@id": canonical + "#webpage",
                    "url": canonical,
                    "name": title,
                    "description": meta_desc,
                    "inLanguage": "ja-JP",
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": 1,
                            "name": "トップ",
                            "item": public_url(base_url, site_prefix, "index.html"),
                        },
                        {
                            "@type": "ListItem",
                            "position": 2,
                            "name": "過去問一覧",
                            "item": hub_item_url,
                        },
                        {
                            "@type": "ListItem",
                            "position": 3,
                            "name": heading,
                            "item": canonical,
                        },
                    ],
                },
            ],
        }
        page_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(meta_desc)}">
<link rel="canonical" href="{html.escape(canonical)}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(meta_desc)}">
<meta property="og:url" content="{html.escape(canonical)}">
<script defer src="/site-analytics.js"></script>
<link rel="stylesheet" href="{html.escape(css_href)}">
<script type="application/ld+json">
{json.dumps(json_ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body class="q-static-body">
<header class="q-static-header">
  <p class="q-static-brand"><a href="{html.escape(root_idx)}">{html.escape(BRAND_NAME)}</a>（{html.escape(EXAM_NAME_OFFICIAL)}）</p>
  <nav aria-label="パンくず">
    <ol class="q-breadcrumb">
      <li><a href="{html.escape(root_idx)}">トップ</a></li>
      <li><a href="{html.escape(q_hub_idx)}">過去問一覧</a></li>
      <li aria-current="page">{html.escape(heading)}</li>
    </ol>
  </nav>
</header>
<main class="q-static-main">
  <h1 class="q-h1">{html.escape(heading)}｜過去問一覧</h1>
  {body_main}
  <p class="q-app-link"><a href="{html.escape(root_idx)}#past">アプリで過去問を開く</a></p>
</main>
{render_static_q_footer(rel)}
</body>
</html>
"""
        full_path = out_root / "past" / era_slug / session / "index.html"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(page_html, encoding="utf-8")
        urls_for_sitemap.append(canonical)


def href_past_question_from_hub(era_slug: str, session: str, r: dict) -> str:
    return f"{r['field']}/{r['qwidth']}/index.html"


def eisei2_index_pages(parsed_rows: list[dict], pool_year: dict[tuple[str, str], int]) -> list[dict]:
    """テンプレ build_q_index 用の page dict（既存 q/past/... URL を維持）。"""
    from build_past_question_pages import glossary_links_for_tags, load_glossary_lookup

    glossary_lookup = load_glossary_lookup()
    pages: list[dict] = []
    for r in parsed_rows:
        if r["is_orig"]:
            continue
        era = normalize_era(r["era_raw"])
        bk = month_key_for_pool({"開催年数": r["era_raw"], "開催月": r["month_raw"]})
        py = pool_year[(era, bk)]
        wareki = breadcrumb_label_past(r["era_raw"], r["month_raw"])
        tags: list[str] = []
        pages.append(
            {
                "year": py,
                "year_label": wareki,
                "qno": r["num"],
                "wareki": wareki,
                "category": FIELD_LABEL_JA[r["field"]],
                "stem_plain": r["text"],
                "tags": tags,
                "correct": int(r["ans_display"]),
                "is_exempt": False,
                "is_invalidated": False,
                "app_id": make_id(py, r["num"], r["field"], False),
                "rel_path": f"q/{href_past_question_from_q_index(r)}",
                "glossary_links": glossary_links_for_tags(tags, glossary_lookup),
            }
        )
    return pages


def write_q_past_index(
    out_root: Path,
    parsed_rows: list[dict],
    n_past: int,
    n_orig: int,
    base_url: str,
    site_prefix: str,
) -> None:
    from build_past_question_pages import build_q_index

    pool_rows = [
        {"開催年数": r["era_raw"], "開催月": r["month_raw"]} for r in parsed_rows
    ]
    pool_year, _labels = discover_pool_years(pool_rows)
    index_pages = eisei2_index_pages(parsed_rows, pool_year)
    html_body = build_q_index(index_pages, base_url)
    (out_root / "index.html").write_text(html_body, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="CSV から静的問題ページ q/ を生成")
    ap.add_argument(
        "--base-url",
        default="https://eisei2shu-master.jp",
        help="canonical / sitemap 用の本番オリジン（末尾スラッシュ不要）",
    )
    ap.add_argument(
        "--site-prefix",
        default="",
        help="GitHub Pages のプロジェクトサイト時など（例: my-repo）。ユーザサイトなら空",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="既定: リポジトリ直下の q/",
    )
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    out_root = args.out_dir or (repo_root / "q")
    data_dir = repo_root / "data"
    csv_paths = [
        data_dir / "eisei2_past_questions.csv",
        data_dir / "eisei2_original_questions.csv",
    ]
    paths = [p for p in csv_paths if p.exists()]
    if not paths:
        print("data/*.csv が見つかりません。", file=sys.stderr)
        sys.exit(1)

    rows_in: list[dict] = []
    for p in paths:
        rows_in.extend(load_rows(p))

    parsed: list[dict] = []
    for i, row in enumerate(rows_in):
        try:
            parsed.append(parse_row(row, i + 2))
        except Exception as e:
            print(f"{e}（{paths} 合算 行 {i + 2}）", file=sys.stderr)
            sys.exit(1)

    widths = compute_widths(parsed)
    for r in parsed:
        r["qwidth"] = format_qwidth(r["num"], widths[r["group_key"]])

    seen_paths: set[str] = set()
    base_url = args.base_url.rstrip("/")
    site_prefix = args.site_prefix.strip("/").strip()

    pool_rows = [
        {"開催年数": r["era_raw"], "開催月": r["month_raw"]} for r in parsed
    ]
    pool_year, _pool_labels = discover_pool_years(pool_rows)
    all_index_pages = eisei2_index_pages(parsed, pool_year)
    from build_past_question_pages import load_glossary_lookup, load_guide_articles

    glossary_lookup = load_glossary_lookup()
    guides = load_guide_articles()
    explanation_meta = load_explanation_meta(data_dir)
    if not explanation_meta:
        print(
            f"warning: {EXPLANATION_META_CSV} がありません。"
            " tools/enrich_eisei2_past_explanations.py を先に実行してください。",
            file=sys.stderr,
        )

    # 出力先を空にしてから生成
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True)

    urls_for_sitemap: list[str] = []

    n_past = n_orig = 0
    for r in parsed:
        r["explanation_meta"] = explanation_meta
        if r["is_orig"]:
            rel = Path(
                relative_url_path_orig(r["session_or_pool"], r["field"], r["qwidth"])
            )
            n_orig += 1
        else:
            rel = Path(
                relative_url_path_past(r["era_slug"], r["session_or_pool"], r["field"], r["qwidth"])
            )
            n_past += 1

        sp = str(rel).replace("/index.html", "").replace("\\", "/")
        web_dir = sp + "/"
        if site_prefix:
            canonical = f"{base_url}/{site_prefix}/{web_dir}"
        else:
            canonical = f"{base_url}/{web_dir}"
        canonical = canonical.replace("/./", "/")

        r["base_url"] = base_url
        r["site_prefix"] = site_prefix
        r["canonical"] = canonical

        key = str(rel).replace("\\", "/")
        if key in seen_paths:
            print(f"重複パス: {key}", file=sys.stderr)
            sys.exit(1)
        seen_paths.add(key)

        if rel.parts[0] != "q":
            print(f"内部エラー: 想定外のパス {rel}", file=sys.stderr)
            sys.exit(1)
        rel_under_q = Path(*rel.parts[1:])
        full_path = out_root / rel_under_q
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(
            build_question_html(
                r, rel, all_index_pages, pool_year, glossary_lookup, guides
            ),
            encoding="utf-8",
        )
        urls_for_sitemap.append(canonical)

    hub_canonical = public_url(base_url, site_prefix, "q/index.html")
    static_urls = [
        public_url(base_url, site_prefix, ""),
        public_url(base_url, site_prefix, "about.html"),
        public_url(base_url, site_prefix, "privacy-terms.html"),
    ]
    for rel_static in (
        "related-sites.html",
        "terms/index.html",
        "articles/index.html",
    ):
        if (repo_root / rel_static).is_file():
            static_urls.append(public_url(base_url, site_prefix, rel_static))
    static_urls.append(hub_canonical)
    all_sitemap_urls = static_urls + urls_for_sitemap

    sitemap_lastmod = dt.datetime.now(dt.timezone.utc).date().isoformat()
    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in sorted(set(all_sitemap_urls)):
        sitemap_lines.append("  <url>")
        sitemap_lines.append(f"    <loc>{xml_escape(u)}</loc>")
        sitemap_lines.append(f"    <lastmod>{xml_escape(sitemap_lastmod)}</lastmod>")
        sitemap_lines.append("    <changefreq>monthly</changefreq>")
        sitemap_lines.append("  </url>")
    sitemap_lines.append("</urlset>")
    root_sitemap_path = repo_root / "sitemap.xml"
    root_sitemap_path.write_text("\n".join(sitemap_lines) + "\n", encoding="utf-8")

    robots_body = (
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {public_url(base_url, site_prefix, 'sitemap.xml')}\n"
    )
    (repo_root / "robots.txt").write_text(robots_body, encoding="utf-8")

    write_session_hubs(out_root, parsed, base_url, site_prefix, urls_for_sitemap)
    write_q_past_index(out_root, parsed, n_past, n_orig, base_url, site_prefix)

    print(
        f"生成完了: {len(seen_paths)} 問 + q/index.html（過去問一覧）+ {root_sitemap_path.name} + robots.txt → {out_root} ほか"
    )


if __name__ == "__main__":
    main()
