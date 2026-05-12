#!/usr/bin/env python3
"""
用語→記事URLの静的インデックス terms/index.html を生成する（SEO用）。
- ソース: docs/glossary-article-slugs.json（用語名→スラッグ）
- カテゴリ: docs/glossary-terms-checklist.csv の「カテゴリ」「用語」列（無ければ JSON の順）
- 実ファイルが terms-dir にある *.html のみ掲載（index.html は除外）
"""
from __future__ import annotations

import argparse
import csv
import html
import json
from collections import defaultdict
from pathlib import Path


CAT_ORDER = ("関係法令", "労働衛生", "労働生理")


def load_term_category(csv_path: Path) -> dict[str, str]:
    if not csv_path.is_file():
        return {}
    out: dict[str, str] = {}
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if len(rows) < 2:
        return {}
    header = [str(c).strip() for c in rows[0]]
    try:
        ic = header.index("カテゴリ")
        it = header.index("用語")
    except ValueError:
        return {}
    for r in rows[1:]:
        if len(r) <= max(ic, it):
            continue
        term = str(r[it]).strip()
        cat = str(r[ic]).strip()
        if term and term not in out:
            out[term] = cat
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--slug-json", type=Path, required=True)
    p.add_argument("--csv", type=Path, help="glossary-terms-checklist.csv（カテゴリ付与用）")
    p.add_argument("--terms-dir", type=Path, required=True, help="公開用 terms（*.html が並ぶディレクトリ）")
    p.add_argument("--out", type=Path, required=True, help="例: public_site/terms/index.html")
    p.add_argument("--base", default="https://eisei2shu-master.jp", help="canonical / JSON-LD 用（末尾スラッシュなし）")
    args = p.parse_args()

    base = str(args.base).rstrip("/")
    terms_dir: Path = args.terms_dir
    if not terms_dir.is_dir():
        raise SystemExit(f"terms-dir が存在しません: {terms_dir}")

    slug_map: dict[str, str] = json.loads(args.slug_json.read_text(encoding="utf-8"))
    if not isinstance(slug_map, dict):
        raise SystemExit("slug-json はオブジェクト形式の JSON である必要があります")

    term_cat = load_term_category(args.csv) if args.csv else {}

    rows: list[tuple[str, str, str]] = []
    for term, slug in slug_map.items():
        slug = str(slug).strip()
        term = str(term).strip()
        if not slug or not term:
            continue
        fp = terms_dir / f"{slug}.html"
        if not fp.is_file():
            continue
        cat = term_cat.get(term, "その他")
        rows.append((cat, term, slug))

    if not rows:
        raise SystemExit("掲載対象の HTML が1件もありません（slug-json と terms-dir を確認）")

    def sort_key(t: tuple[str, str, str]) -> tuple[int, str, str]:
        cat, term, slug = t
        try:
            ci = CAT_ORDER.index(cat)
        except ValueError:
            ci = len(CAT_ORDER)
        return (ci, term, slug)

    rows.sort(key=sort_key)

    by_cat: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for cat, term, slug in rows:
        by_cat[cat].append((term, slug))

    list_items_ld: list[dict] = []
    pos = 1
    for cat, term, slug in sorted(rows, key=sort_key):
        url = f"{base}/terms/{slug}.html"
        list_items_ld.append(
            {
                "@type": "ListItem",
                "position": pos,
                "name": term,
                "item": url,
            }
        )
        pos += 1

    ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "第二種衛生管理者試験 用語解説一覧",
        "description": "試験で出やすい用語ごとの解説記事への索引です。",
        "numberOfItems": len(rows),
        "itemListElement": list_items_ld,
    }

    body_sections: list[str] = []
    cat_keys = [c for c in CAT_ORDER if c in by_cat]
    for c in by_cat:
        if c not in cat_keys and c != "その他":
            cat_keys.append(c)
    if "その他" in by_cat:
        cat_keys.append("その他")

    for cat in cat_keys:
        items = by_cat.get(cat)
        if not items:
            continue
        body_sections.append(f'<section class="terms-idx-cat" aria-labelledby="cat-{html.escape(cat, quote=True)}">')
        body_sections.append(f'  <h2 id="cat-{html.escape(cat, quote=True)}">{html.escape(cat)}</h2>')
        body_sections.append('  <ul class="terms-idx-list">')
        for term, slug in sorted(items, key=lambda x: x[0]):
            href = f"/terms/{html.escape(slug, quote=True)}.html"
            body_sections.append(
                f'    <li><a href="{href}">{html.escape(term)}</a></li>'
            )
        body_sections.append("  </ul>")
        body_sections.append("</section>")

    body_html = "\n".join(body_sections)
    ld_json = json.dumps(ld, ensure_ascii=False, indent=2)

    page = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>用語解説一覧（全記事索引）｜二衛マスター（第二種衛生管理者試験）</title>
<meta name="description" content="第二種衛生管理者試験の重要用語を一覧し、各用語の解説記事へリンクします。関係法令・労働衛生・労働生理の語句を網羅的に整理しています。">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{html.escape(base + "/terms/", quote=True)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{html.escape(base + "/terms/", quote=True)}">
<meta property="og:title" content="用語解説一覧（全記事索引）｜二衛マスター">
<meta property="og:description" content="試験で出やすい用語ごとの解説記事への索引です。">
<meta property="og:locale" content="ja_JP">
<script type="application/ld+json">
{ld_json}
</script>
<style>
body{{font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Hiragino Sans","Noto Sans JP",sans-serif;line-height:1.65;margin:0;background:#f6f7f9;color:#1a1a1a;}}
.wrap{{max-width:880px;margin:0 auto;padding:24px 18px 48px;}}
header{{margin-bottom:28px;}}
h1{{font-size:1.45rem;margin:0 0 10px;}}
.lead{{font-size:0.95rem;color:#444;margin:0;}}
.breadcrumb{{font-size:0.88rem;margin-bottom:18px;color:#555;}}
.breadcrumb a{{color:#0b57d0;}}
.terms-idx-cat{{margin-top:28px;}}
.terms-idx-cat h2{{font-size:1.1rem;border-bottom:2px solid #dde1e7;padding-bottom:6px;margin:0 0 12px;}}
.terms-idx-list{{list-style:none;padding:0;margin:0;columns:2;column-gap:28px;}}
@media(max-width:640px){{.terms-idx-list{{columns:1;}}}}
.terms-idx-list li{{break-inside:avoid;margin:0 0 8px 0;padding-left:0;}}
.terms-idx-list a{{color:#0b57d0;text-decoration:none;font-weight:500;}}
.terms-idx-list a:hover{{text-decoration:underline;}}
footer{{margin-top:40px;font-size:0.85rem;color:#666;border-top:1px solid #dde1e7;padding-top:16px;}}
</style>
</head>
<body>
<div class="wrap">
<header>
<nav class="breadcrumb" aria-label="パンくず"><a href="/">トップ</a> ／ 用語解説一覧</nav>
<h1>用語解説一覧（全記事索引）</h1>
<p class="lead">第二種衛生管理者試験で頻出の用語を科目別に並べ、各用語の<strong>解説記事（静的HTML）</strong>へ直接リンクします。検索エンジンは本ページと各記事のリンク関係を確実に辿れます。</p>
</header>
<main>
{body_html}
</main>
<footer>
<p>アプリ内のインタラクティブな用語カードは <a href="/">トップ</a> の「用語解説」からも利用できます。</p>
</footer>
</div>
</body>
</html>
"""

    out: Path = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"generate_terms_index_html.py: {len(rows)} 件 -> {out}")


if __name__ == "__main__":
    main()
