#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""試験ガイド全件の品質監査（CSV + 生成 HTML）。"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.glossary_link_lib import article_term_lookup, load_glossary_entries

GUIDE_CSV = ROOT / "data" / "guide_articles.csv"
ARTICLES_DIR = ROOT / "articles"

GENERIC_CORE = "この見出しの内容が他のテーマと組み合わされて出題されることがあります"
BOILER_LEAD_PREFIX = "本記事は第二種衛生管理者試験に特化し"
ARROW_PLAIN_RE = re.compile(r"(?<![>])→\s*[^<\[]")
HREF_RE = re.compile(r"""href\s*=\s*(["'])(.*?)\1""", re.IGNORECASE)


def body_len(row: dict) -> int:
    return sum(len(row.get(f"section_{i}_body") or "") for i in range(1, 9))


def section_count(row: dict) -> int:
    return sum(
        1
        for i in range(1, 9)
        if (row.get(f"section_{i}_heading") or "").strip()
        and (row.get(f"section_{i}_body") or "").strip()
    )


def load_legacy_body_lengths() -> dict[str, int]:
    """git 1887be7 の旧 flat HTML から本文文字数（概算）。"""
    out: dict[str, int] = {}
    try:
        names = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", "1887be7", "articles"],
            text=True,
            cwd=ROOT,
        ).splitlines()
    except subprocess.CalledProcessError:
        return out
    for name in names:
        if not name.endswith(".html") or name.endswith("/index.html"):
            continue
        slug = Path(name).stem
        if slug in ("index",):
            continue
        try:
            html = subprocess.check_output(
                ["git", "show", f"1887be7:{name}"],
                text=True,
                cwd=ROOT,
                errors="replace",
            )
        except subprocess.CalledProcessError:
            continue
        # article-body 内テキスト量の粗い近似
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        out[slug] = len(text)
    return out


def audit_html(slug: str, lookup: dict[str, str]) -> list[str]:
    issues: list[str] = []
    html_path = ARTICLES_DIR / slug / "index.html"
    if not html_path.is_file():
        return [f"HTML missing: {html_path.relative_to(ROOT)}"]

    html = html_path.read_text(encoding="utf-8")
    main = html
    if "seo-article-card" in html:
        m = re.search(
            r'<article[^>]*class="[^"]*seo-article-card[^"]*"[^>]*>(.*)</article>',
            html,
            re.DOTALL,
        )
        if m:
            main = m.group(1)

    if ARROW_PLAIN_RE.search(main):
        issues.append("plain「→」text without <a> (article body)")

    # 頻出用語一覧: 用語名が <a> なしで並んでいる
    sec = re.search(
        r'aria-labelledby="article-sec-1"[^>]*>.*?頻出用語一覧.*?</section>',
        main,
        re.DOTALL,
    )
    if sec:
        block = sec.group(0)
        if "<ul>" in block:
            for li in re.findall(r"<li>(.*?)</li>", block, re.DOTALL):
                if li.strip() and "<a " not in li and "→" not in li:
                    issues.append(f"unlinked list item: {li.strip()[:40]}")
        elif re.search(r"<p>[^<]*(?:<br>)?[^<]{2,}</p>", block) and "terms/" not in block[:500]:
            issues.append("term list not in <ul> with term links")

    # 関連用語ボックス（ガイドには通常なし）— related-box 内のプレーンテキスト
    for box in re.findall(
        r'<div class="related-box"[^>]*>.*?</div>\s*</div>',
        main,
        re.DOTALL,
    ):
        if "related-link-static" in box:
            issues.append("related-link-static (no href)")

    # 内部リンク切れ（articles/terms 相対のみ）
    for href in HREF_RE.findall(main):
        h = href[1].strip() if isinstance(href, tuple) else href
        if not h or h.startswith(("#", "http", "mailto:")):
            continue
        if h.startswith("../"):
            # URL フラグメント(#...)・クエリ(?...)を除いてファイル存在を判定する
            path_part = h.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue
            target = (html_path.parent / path_part).resolve()
            if not target.exists():
                issues.append(f"broken href: {h}")

    return issues


def main() -> int:
    with GUIDE_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    lookup = article_term_lookup()
    legacy = load_legacy_body_lengths()

    report: dict[str, list[str]] = {
        "generic_addon_csv": [],
        "boilerplate_lead": [],
        "thin_csv_body_lt200": [],
        "legacy_much_shorter": [],
        "html_issues": [],
        "no_html": [],
    }

    for row in rows:
        slug = (row.get("slug") or "").strip()
        if not slug:
            continue

        lead = row.get("lead") or ""
        if BOILER_LEAD_PREFIX in lead:
            report["boilerplate_lead"].append(slug)

        bl = body_len(row)
        if bl < 200:
            report["thin_csv_body_lt200"].append(f"{slug} ({bl} chars)")

        for i in range(1, 9):
            if GENERIC_CORE in (row.get(f"section_{i}_body") or ""):
                report["generic_addon_csv"].append(f"{slug}:sec{i}")

        leg = legacy.get(slug)
        if leg and bl < leg * 0.6:
            report["legacy_much_shorter"].append(f"{slug} csv={bl} legacy~={leg}")

        hi = audit_html(slug, lookup)
        if not (ARTICLES_DIR / slug / "index.html").is_file():
            report["no_html"].append(slug)
        elif hi:
            for h in hi:
                report["html_issues"].append(f"{slug}: {h}")

    print(f"Audited {len(rows)} guide articles\n")
    total_problems = 0
    for key, items in report.items():
        print(f"## {key}: {len(items)}")
        total_problems += len(items)
        for x in items[:20]:
            print(f"  - {x}")
        if len(items) > 20:
            print(f"  ... and {len(items) - 20} more")
        print()

    if total_problems == 0:
        print("OK: No issues found in full audit.")
        return 0
    print(f"TOTAL issues: {total_problems}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
