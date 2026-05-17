#!/usr/bin/env python3
"""
build.py — MDファイルをHTMLに変換するビルドスクリプト
使い方: python build.py
"""

import os
import re
import glob
import html
import frontmatter
import markdown
from datetime import datetime

# ===== 設定 =====
SITE_URL = "https://eisei2shu-master.jp"
ARTICLES_DIR = "articles"                    # MDファイルの置き場
OUTPUT_DIR = "dist/terms"                    # 出力先
TEMPLATE_FILE = "template.html"

AUTHOR_NAME = "二衛マスター編集部"
AUTHOR_PROFILE = "第二種衛生管理者試験の学習用語、過去問の復習導線、試験ガイドを整理する編集チームです。"
REVIEWER_NAME = "二衛マスター編集部"
REVIEWER_PROFILE = "公開前に公式情報、法令情報、サイト内の関連ページとの整合性を確認しています。"
PRIMARY_SOURCES = (
    ("安全衛生技術試験協会", "https://www.exam.or.jp/"),
    ("厚生労働省 職場のあんぜんサイト", "https://anzeninfo.mhlw.go.jp/"),
    ("e-Gov法令検索", "https://elaws.e-gov.go.jp/"),
)
CATEGORY_GUIDES = {
    "関係法令": ("/articles/kankei-horei-matome.html", "関係法令の頻出ポイントまとめ"),
    "労働衛生": ("/articles/rodo-eisei-matome.html", "労働衛生の頻出ポイントまとめ"),
    "労働生理": ("/articles/rodo-seiri-matome.html", "労働生理の頻出ポイントまとめ"),
}

# =================


def load_template():
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        return f.read()


def md_to_html(md_text):
    """MarkdownをHTMLに変換（テーブル・改行対応）"""
    return markdown.markdown(
        md_text,
        extensions=["tables", "nl2br", "fenced_code"]
    )


def extract_related_links(html_body):
    """
    記事末尾の「関連過去問」セクションをHTMLから除去する。
    過去問リンクはリンク切れが発生しやすく、UXを損なうため現状は表示しない。
    """
    # <h2>が「関連過去問」「関連する過去問」を含むセクションを検出
    pattern = r'<h2[^>]*>(?:(?!</h2>).)*関連(?:する)?過去問(?:(?!</h2>).)*</h2>(.*?)(?=<h2|$)'
    match = re.search(pattern, html_body, re.DOTALL | re.IGNORECASE)
    if not match:
        return html_body, ""

    # article_body からセクションごと除去
    full_section = match.group(0)
    clean_body = html_body.replace(full_section, "").strip()
    return clean_body, ""


def escape_text(value):
    return html.escape(str(value or ""), quote=True)


def strip_exam_suffix(text):
    """ページ上の表示用に、タイトル末尾の試験名補足を外す。"""
    text = str(text or "").strip()
    text = re.sub(r"【.*?】", "", text).strip()
    return text


def term_label(h1, title):
    label = strip_exam_suffix(h1 or title)
    label = re.sub(r"とは[？?]?.*$", "", label).strip()
    return label or strip_exam_suffix(title)


def add_heading_ids(html_body):
    """本文H2に目次リンク用のIDを付ける。"""
    headings = []
    count = 0

    def repl(match):
        nonlocal count
        attrs = match.group(1) or ""
        text = re.sub(r"<[^>]+>", "", match.group(2)).strip()
        if "id=" in attrs:
            heading_id_match = re.search(r'id=["\']([^"\']+)["\']', attrs)
            heading_id = heading_id_match.group(1) if heading_id_match else f"section-{count + 1}"
            headings.append((heading_id, text))
            return match.group(0)
        count += 1
        heading_id = f"term-section-{count}"
        headings.append((heading_id, text))
        return f'<h2{attrs} id="{heading_id}">{match.group(2)}</h2>'

    return re.sub(r"<h2([^>]*)>(.*?)</h2>", repl, html_body, flags=re.DOTALL), headings


def build_toc(existing_headings):
    items = [
        ("term-reliability", "この記事の信頼性について"),
        ("term-official-info", "公式情報の確認"),
        ("term-basic-info", "記事の基本情報"),
        ("term-can-do", "この記事でできること"),
    ]
    items.extend(existing_headings)
    items.extend([
        ("term-faq", "よくある質問"),
        ("term-related", "関連記事"),
    ])
    links = "\n".join(
        f'      <li><a href="#{escape_text(anchor)}">{escape_text(label)}</a></li>'
        for anchor, label in items
        if label
    )
    return f"""<nav class="term-toc" aria-label="目次">
  <h2>目次</h2>
  <ol>
{links}
  </ol>
</nav>"""


def build_top_seo_sections(meta, h1, title, existing_headings):
    category = meta.get("category", "用語解説")
    updated = meta.get("updated", datetime.today().strftime("%Y-%m-%d"))
    label = term_label(h1, title)
    sources = "\n".join(
        f'      <li><a href="{escape_text(url)}" rel="nofollow noopener" target="_blank">{escape_text(name)}</a></li>'
        for name, url in PRIMARY_SOURCES
    )
    toc = build_toc(existing_headings)
    return f"""{toc}

<section id="term-reliability" class="term-info-box">
  <h2>この記事の信頼性について</h2>
  <dl class="term-fact-list">
    <div><dt>執筆者</dt><dd>{escape_text(AUTHOR_NAME)}。{escape_text(AUTHOR_PROFILE)}</dd></div>
    <div><dt>確認者</dt><dd>{escape_text(REVIEWER_NAME)}。{escape_text(REVIEWER_PROFILE)}</dd></div>
    <div><dt>事実確認日</dt><dd>{escape_text(updated)}</dd></div>
    <div><dt>更新方針</dt><dd>試験要項、公式ページ、関係法令に変更が確認されたタイミングで本文と参照元を見直します。</dd></div>
  </dl>
</section>

<section id="term-official-info" class="term-info-box">
  <h2>公式情報の確認</h2>
  <p>{escape_text(label)}は、第二種衛生管理者試験の学習で押さえたい用語です。制度、数値、義務の有無は年度や法令改正で変わることがあるため、受験前には公式情報も確認してください。</p>
  <ul>
{sources}
  </ul>
</section>

<section id="term-basic-info" class="term-info-box">
  <h2>記事の基本情報</h2>
  <dl class="term-fact-list">
    <div><dt>対象試験</dt><dd>第二種衛生管理者試験</dd></div>
    <div><dt>分野</dt><dd>{escape_text(category)}</dd></div>
    <div><dt>記事種別</dt><dd>用語詳細記事</dd></div>
    <div><dt>検索意図</dt><dd>{escape_text(label)}の意味、試験で問われる観点、復習時の確認ポイントを整理すること。</dd></div>
  </dl>
</section>

<section id="term-can-do" class="term-info-box">
  <h2>この記事でできること</h2>
  <p>この記事では、{escape_text(label)}の基本的な意味を確認し、表や頻出ポイントを使って試験で迷いやすい部分を整理できます。読み終えたら、関連用語と過去問を合わせて確認し、知識を選択肢で使える状態に近づけてください。</p>
  <ul>
    <li>{escape_text(label)}の定義と位置づけを確認する</li>
    <li>表で重要な条件や数値を整理する</li>
    <li>頻出の誤り選択肢を復習する</li>
    <li>関連する用語解説や過去問へ進む</li>
  </ul>
</section>"""


def build_bottom_seo_sections(meta, h1, title):
    category = meta.get("category", "")
    label = term_label(h1, title)
    guide_href, guide_label = CATEGORY_GUIDES.get(
        category,
        ("/articles/shiken-kamoku.html", "試験科目と出題範囲の確認"),
    )
    return f"""<section id="term-faq" class="term-info-box">
  <h2>よくある質問</h2>
  <details open>
    <summary>{escape_text(label)}は丸暗記だけで足りますか？</summary>
    <p>用語そのものを覚えるだけでなく、試験では「どの場面で使うか」「何と混同しやすいか」まで問われます。本文の表と頻出ポイントを確認したあと、過去問で選択肢の言い換えに慣れておくと復習しやすくなります。</p>
  </details>
  <details open>
    <summary>公式情報も確認した方がよいですか？</summary>
    <p>数値、対象業務、保存期間、選任要件などが関係する用語は、公式情報の確認が特に重要です。この記事は学習用の整理として使い、受験前や実務で使う前には安全衛生技術試験協会、厚生労働省、e-Gov法令検索なども確認してください。</p>
  </details>
</section>

<section id="term-related" class="term-info-box">
  <h2>関連記事</h2>
  <ul>
    <li><a href="/terms/">用語解説一覧で関連用語を探す</a></li>
    <li><a href="{escape_text(guide_href)}">{escape_text(guide_label)}</a></li>
    <li><a href="/q/">過去問一覧で出題形式を確認する</a></li>
  </ul>
</section>"""


def insert_after_lead(html_body, inserted_html):
    """リード直後に目次とSEO補足ブロックを入れる。"""
    match = re.search(r"\s*<hr\s*/?>\s*", html_body, flags=re.IGNORECASE)
    if not match:
        return f"{inserted_html}\n\n{html_body}"
    return f"{html_body[:match.start()].rstrip()}\n\n{inserted_html}\n\n{html_body[match.end():].lstrip()}"


def build_page(md_path, template):
    post = frontmatter.load(md_path)
    meta = post.metadata

    slug = meta.get("slug", os.path.splitext(os.path.basename(md_path))[0])
    title = meta.get("title", "")
    description = meta.get("description", "")
    category = meta.get("category", "")
    updated = meta.get("updated", datetime.today().strftime("%Y-%m-%d"))
    canonical = f"{SITE_URL}/terms/{slug}.html"

    # H1テキスト（タイトルから最初の「とは」前後を取る）
    h1_match = re.match(r"^(.+?)(?:【|　|$)", title)
    h1 = h1_match.group(1).strip() if h1_match else title

    # MD → HTML
    body_html = md_to_html(post.content)

    # 先頭のH1タグを除去（article-titleで代替表示するため）
    body_html = re.sub(r'^<h1[^>]*>.*?</h1>\s*', '', body_html, flags=re.DOTALL)

    # 関連過去問ボックスを抽出・分離
    body_html, related_box = extract_related_links(body_html)
    body_html, headings = add_heading_ids(body_html)
    top_sections = build_top_seo_sections(meta, h1, title, headings)
    bottom_sections = build_bottom_seo_sections(meta, h1, title)
    body_html = insert_after_lead(body_html, top_sections)
    body_html = f"{body_html}\n\n{bottom_sections}"

    # テンプレートに埋め込み
    html = template
    html = html.replace("{{title}}", title)
    html = html.replace("{{description}}", description)
    html = html.replace("{{canonical}}", canonical)
    html = html.replace("{{site_url}}", SITE_URL)
    html = html.replace("{{h1}}", h1)
    html = html.replace("{{category}}", category)
    html = html.replace("{{updated}}", str(updated))
    html = html.replace("{{body}}", body_html)
    html = html.replace("{{related_box}}", related_box)

    # 出力
    out_path = os.path.join(OUTPUT_DIR, f"{slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    return slug, out_path


def build_sitemap(slugs: list, updated_map: dict):
    """生成したページのsitemap.xmlを dist/ に出力する"""
    today = datetime.today().strftime("%Y-%m-%d")

    urls = []

    # トップページ
    urls.append(f"""  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>""")

    # 用語一覧ページ
    urls.append(f"""  <url>
    <loc>{SITE_URL}/terms/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    # 各用語ページ
    for slug in slugs:
        lastmod = updated_map.get(slug, today)
        urls.append(f"""  <url>
    <loc>{SITE_URL}/terms/{slug}.html</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>""")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "\n".join(urls)
    sitemap += "\n</urlset>\n"

    sitemap_path = os.path.join("dist", "sitemap.xml")
    os.makedirs("dist", exist_ok=True)
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap)

    return sitemap_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    template = load_template()

    md_files = sorted(glob.glob(os.path.join(ARTICLES_DIR, "*.md")))
    if not md_files:
        print("⚠️  articles/ にMDファイルが見つかりませんでした。")
        return

    print(f"📄 {len(md_files)}件のMDファイルを処理します...\n")
    success, failed = [], []
    updated_map = {}

    for md_path in md_files:
        try:
            slug, out_path = build_page(md_path, template)
            print(f"  ✅ {os.path.basename(md_path)} → {out_path}")
            success.append(slug)

            # updated日付を記録（サイトマップ用）
            post = frontmatter.load(md_path)
            updated = post.metadata.get("updated", "")
            if updated:
                updated_map[slug] = str(updated)

        except Exception as e:
            print(f"  ❌ {os.path.basename(md_path)}: {e}")
            failed.append(md_path)

    print(f"\n完了: {len(success)}件成功", end="")
    if failed:
        print(f" / {len(failed)}件失敗: {failed}")
    else:
        print()

    # サイトマップ生成
    if success:
        sitemap_path = build_sitemap(success, updated_map)
        print(f"🗺️  サイトマップ生成: {sitemap_path}（{len(success) + 2}件のURL）")
        print(f"\n次のステップ：")
        print(f"  Search Console でサイトマップを送信してください")
        print(f"  URL: {SITE_URL}/sitemap.xml")


if __name__ == "__main__":
    main()
