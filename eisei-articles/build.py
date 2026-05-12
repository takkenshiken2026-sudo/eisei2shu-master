#!/usr/bin/env python3
"""
build.py — MDファイルをHTMLに変換するビルドスクリプト
使い方: python build.py
"""

import os
import re
import glob
import frontmatter
import markdown
from datetime import datetime

# ===== 設定 =====
SITE_URL = "https://dai2shu-eisei.example"   # ← 本番ドメインに変更する
ARTICLES_DIR = "articles"                    # MDファイルの置き場
OUTPUT_DIR = "dist/terms"                    # 出力先
TEMPLATE_FILE = "template.html"

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
    記事末尾の「関連過去問へのリンク」セクションをHTMLから抽出し、
    専用デザインのボックスに変換して返す。
    元のセクションは article_body から除去する。
    """
    # <h2>が「関連過去問」を含むセクションを検出
    pattern = r'<h2[^>]*>.*?関連過去問.*?</h2>(.*?)(?=<h2|$)'
    match = re.search(pattern, html_body, re.DOTALL | re.IGNORECASE)
    if not match:
        return html_body, ""

    links_block = match.group(1)
    # article_body からセクションごと除去
    full_section = match.group(0)
    clean_body = html_body.replace(full_section, "").strip()

    # <li> 内の <a> を抽出
    link_pattern = r'<a href="([^"]+)">([^<]+)</a>'
    links = re.findall(link_pattern, links_block)

    if not links:
        return clean_body, ""

    link_items = ""
    for href, text in links:
        link_items += f'''
    <a href="{href}" class="related-link">
      <svg viewBox="0 0 24 24"><path d="M9 18l6-6-6-6"/></svg>
      {text}
    </a>'''

    related_box = f'''
  <div class="related-box">
    <div class="related-box-title">関連過去問を解く</div>
    <div class="related-links">{link_items}
    </div>
  </div>'''

    return clean_body, related_box


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
