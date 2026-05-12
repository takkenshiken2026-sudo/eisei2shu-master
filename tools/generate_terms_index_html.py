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

    def term_key(t: tuple[str, str]) -> str:
        term, _slug = t
        return term

    for cat in cat_keys:
        items = by_cat.get(cat)
        if not items:
            continue
        body_sections.append(f'<section class="terms-idx-cat" aria-labelledby="cat-{html.escape(cat, quote=True)}">')
        body_sections.append(f'  <h2 id="cat-{html.escape(cat, quote=True)}">{html.escape(cat)}</h2>')
        body_sections.append('  <ul class="terms-idx-list">')
        for term, slug in sorted(items, key=term_key):
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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #ffffff;
  --bg2: #f4f4f5;
  --bg3: #e4e4e7;
  --text: #111111;
  --text2: #555555;
  --text3: #888888;
  --ink: #333333;
  --border: rgba(0,0,0,0.10);
  --border2: rgba(0,0,0,0.18);
  --font: 'Noto Sans JP', sans-serif;
  --r: 6px;
  --r2: 10px;
  --sh: 0 1px 3px rgba(0,0,0,0.07);
  --max-w: 1160px;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: var(--font);
  font-size: 16px;
  line-height: 1.8;
  background: #f0f0f1;
  color: var(--text);
  -webkit-font-smoothing: antialiased;
}}
a {{ color: var(--ink); text-decoration: underline; text-underline-offset: 3px; }}
a:hover {{ opacity: 0.9; }}

/* ===== HEADER ===== */
.site-header {{
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 50;
}}
.site-header-inner {{
  max-width: var(--max-w);
  margin: 0 auto;
  padding: 0 20px;
  height: 52px;
  display: flex;
  align-items: center;
  gap: 12px;
}}
.header-back {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text3);
  text-decoration: none;
  padding: 6px 10px;
  border-radius: var(--r);
  border: 1px solid var(--border2);
  background: var(--bg);
  transition: all .15s;
}}
.header-back:hover {{ background: var(--bg2); color: var(--text); opacity: 1; }}
.header-back svg {{ width: 14px; height: 14px; stroke: currentColor; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }}
.header-logo {{
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  text-decoration: none;
}}
.header-sep {{ color: var(--text3); font-size: 13px; }}

/* ===== LAYOUT ===== */
.container {{
  max-width: var(--max-w);
  margin: 0 auto;
  padding: 20px 20px 56px;
}}
.page-title {{
  font-size: 1.55rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 12px 0 10px;
}}
.lead {{
  font-size: 15px;
  color: var(--text2);
  margin-bottom: 16px;
  line-height: 1.7;
}}
.meta-row {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px 12px;
  align-items: center;
  margin: 16px 0 18px;
}}
.pill {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text2);
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 6px 10px;
}}
.search {{
  flex: 1;
  min-width: min(420px, 100%);
  display: flex;
  gap: 10px;
  align-items: center;
}}
.search input {{
  width: 100%;
  padding: 10px 12px;
  border-radius: var(--r2);
  border: 1.5px solid var(--border2);
  background: var(--bg);
  color: var(--text);
  outline: none;
  font-size: 15px;
}}
.search input:focus {{ border-color: rgba(0,0,0,0.35); }}
/* ===== LIST ===== */
.section {{
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r2);
  box-shadow: var(--sh);
  padding: 18px 18px 6px;
  margin-top: 14px;
}}
.terms-idx-cat {{
  margin-top: 16px;
}}
.terms-idx-cat:first-child {{
  margin-top: 4px;
}}
.terms-idx-cat h2 {{
  font-size: 14px;
  font-weight: 800;
  color: var(--ink);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
  margin-bottom: 10px;
}}
.terms-idx-list {{
  list-style: none;
  columns: 2;
  column-gap: 22px;
  margin-bottom: 10px;
}}
@media (max-width: 760px) {{
  .terms-idx-list {{ columns: 1; }}
  .search {{ min-width: 100%; }}
}}
.terms-idx-list li {{
  break-inside: avoid;
  margin: 0 0 8px;
}}
.terms-idx-list a {{
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  text-decoration: none;
  color: var(--ink);
  font-weight: 400;
  font-size: 14px;
}}
.terms-idx-list a:hover {{ text-decoration: underline; }}
.badge {{
  font-size: 11px;
  font-weight: 800;
  color: var(--text3);
  border: 1px solid var(--border);
  background: var(--bg2);
  border-radius: 999px;
  padding: 1px 7px;
}}
.hide {{ display: none !important; }}
.footer {{
  margin-top: 18px;
  font-size: 13px;
  color: var(--text3);
  text-align: center;
}}
</style>
</head>
<body>
<header class="site-header">
  <div class="site-header-inner">
    <a class="header-back" href="/">
      <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M9.5 3.5L5 8l4.5 4.5"/></svg>
      トップへ
    </a>
    <a class="header-logo" href="/">二衛マスター</a>
    <span class="header-sep">/</span>
    <span style="font-size:13px;color:var(--text3);font-weight:700">用語解説一覧</span>
  </div>
</header>

<main class="container">
  <h1 class="page-title">用語解説一覧（全記事索引）</h1>
  <p class="lead">第二種衛生管理者試験で頻出の用語を科目別にまとめています。詳細は各用語の解説記事で確認が可能です。</p>

  <div class="meta-row">
    <span class="pill">全 <span id="terms-total">{len(rows)}</span> 記事</span>
    <div class="search" role="search" aria-label="用語検索">
      <input id="q" type="search" inputmode="search" placeholder="例：WBGT、局所排気装置、衛生委員会…" autocomplete="off">
    </div>
  </div>

  <section class="section" aria-label="用語一覧">
{body_html}
    <div class="footer">
      <span id="terms-hit"></span>
      <div style="margin-top:10px">学習アプリ本体は <a href="/">トップ</a> から利用できます。</div>
    </div>
  </section>
</main>

<script>
(() => {{
  const q = document.getElementById('q');
  const cats = Array.from(document.querySelectorAll('.terms-idx-cat'));
  const totalEl = document.getElementById('terms-total');
  const hitEl = document.getElementById('terms-hit');

  function norm(s) {{
    return (s || '').toString().trim().toLowerCase();
  }}

  function apply() {{
    const query = norm(q.value);
    let shown = 0;

    cats.forEach(sec => {{
      const items = Array.from(sec.querySelectorAll('li'));
      let anyInCat = 0;
      items.forEach(li => {{
        const a = li.querySelector('a');
        const t = norm(a?.textContent || '');
        const ok = (!query || t.includes(query));
        li.classList.toggle('hide', !ok);
        if(ok) {{ anyInCat++; shown++; }}
      }});
      sec.classList.toggle('hide', anyInCat === 0);
    }});

    if(totalEl) totalEl.textContent = String({len(rows)});
    if(hitEl) {{
      hitEl.textContent = query
        ? `表示：${{shown}}件`
        : '';\n    }}\n  }}\n\n  q.addEventListener('input', apply);\n  apply();\n}})();\n</script>
</body>
</html>
"""

    out: Path = args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"generate_terms_index_html.py: {len(rows)} 件 -> {out}")


if __name__ == "__main__":
    main()
