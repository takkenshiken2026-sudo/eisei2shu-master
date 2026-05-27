#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""旧 articles/*.html からセクション本文（表・リスト・リンク）を復元し guide_articles.csv を更新する。"""
from __future__ import annotations

import argparse
import csv
import html
import io
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.guide_link_lib import resolve_legacy_href  # noqa: E402

GUIDE_CSV = ROOT / "data" / "guide_articles.csv"
DEFAULT_GIT_REF = "1887be7"
AFFILIATE_TAG = "アフィリエイト"
SKIP_SLUGS = frozenset(
    {
        "category-kankeihorei",
        "category-rodoeisei",
        "category-rodoseiri",
        "affiliate-smart-vs-onsuku",
        "affiliate-smart-course-guide",
    }
)

TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(text: str) -> str:
    return html.unescape(TAG_RE.sub("", text or "")).strip()


def inline_html_to_md(fragment: str) -> str:
    text = fragment or ""

    def link_repl(match: re.Match[str]) -> str:
        href = resolve_legacy_href(match.group(1))
        label = strip_tags(match.group(2))
        return f"[{label}]({href})"

    text = re.sub(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        link_repl,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</?strong>", "", text, flags=re.IGNORECASE)
    return strip_tags(text)


def html_table_to_csv(table_html: str) -> str:
    rows: list[str] = []
    for tr in re.finditer(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.DOTALL | re.IGNORECASE):
        cells = [
            inline_html_to_md(cell)
            for cell in re.findall(
                r"<t[hd][^>]*>(.*?)</t[hd]>",
                tr.group(1),
                flags=re.DOTALL | re.IGNORECASE,
            )
        ]
        cells = [c for c in cells if c]
        if cells:
            rows.append("|".join(cells))
    if len(rows) < 2:
        return ""
    return "[table]\n" + "\n".join(rows) + "\n[/table]"


def block_html_to_csv(block: str) -> str:
    block = block.strip()
    if not block:
        return ""
    parts: list[str] = []
    pos = 0
    for match in re.finditer(
        r"<table[^>]*>.*?</table>|<ul[^>]*>.*?</ul>|<ol[^>]*>.*?</ol>|<p[^>]*>.*?</p>|→\s*<a[^>]+>.*?</a>",
        block,
        flags=re.DOTALL | re.IGNORECASE,
    ):
        before = block[pos : match.start()].strip()
        if before:
            text = inline_html_to_md(before)
            if text:
                parts.append(text)
        chunk = match.group(0)
        if chunk.lower().startswith("<table"):
            table = html_table_to_csv(chunk)
            if table:
                parts.append(table)
        elif chunk.lower().startswith(("<ul", "<ol")):
            items = [
                inline_html_to_md(li)
                for li in re.findall(r"<li[^>]*>(.*?)</li>", chunk, flags=re.DOTALL | re.IGNORECASE)
            ]
            items = [i for i in items if i]
            if len(items) >= 2:
                parts.append(";".join(items))
            elif items:
                parts.append(items[0])
        elif chunk.lower().startswith("<p"):
            text = inline_html_to_md(chunk)
            if text:
                parts.append(text)
        else:
            text = inline_html_to_md(chunk)
            if text:
                parts.append(text)
        pos = match.end()
    tail = block[pos:].strip()
    if tail:
        text = inline_html_to_md(tail)
        if text:
            parts.append(text)
    if not parts:
        text = inline_html_to_md(block)
        return text
    return "\n\n".join(parts)


def normalize_heading(text: str) -> str:
    text = re.sub(r"【[^】]+】", "", text or "")
    text = re.sub(r"\s+", "", text)
    return text.strip()


def extract_legacy_sections(html_text: str) -> list[tuple[str, str]]:
    start = html_text.find('class="article-body"')
    if start < 0:
        return []
    body = html_text[start : html_text.find("</article>", start)]
    sections: list[tuple[str, str]] = []
    h2_matches = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", body, flags=re.DOTALL | re.IGNORECASE))
    for idx, match in enumerate(h2_matches):
        heading = strip_tags(match.group(1))
        content_start = match.end()
        content_end = h2_matches[idx + 1].start() if idx + 1 < len(h2_matches) else len(body)
        content = block_html_to_csv(body[content_start:content_end])
        if heading and content:
            sections.append((heading, content))
    return sections


def dedupe_repeated_phrases(text: str) -> str:
    phrase = '苦手科目は"丸暗記"より、過去問で出た論点リストを作り、用語ページと往復する復習が効率的です。'
    while phrase + phrase in text:
        text = text.replace(phrase + phrase, phrase)
    # 同一文（40字以上）の連続重複を1回に
    for _ in range(20):
        m = re.search(r"(.{40,}?)(?:\1)+", text)
        if not m:
            break
        text = text.replace(m.group(0), m.group(1), 1)
    return text.strip()


def load_legacy_html(slug: str, git_ref: str) -> str | None:
    path = f"articles/{slug}.html"
    try:
        return subprocess.check_output(
            ["git", "show", f"{git_ref}:{path}"],
            text=True,
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None


def restore_row(row: dict[str, str], git_ref: str) -> bool:
    slug = (row.get("slug") or "").strip()
    if not slug or slug in SKIP_SLUGS:
        return False
    tags = [t.strip() for t in (row.get("tags") or "").split(";") if t.strip()]
    if AFFILIATE_TAG in tags:
        return False
    html_text = load_legacy_html(slug, git_ref)
    if not html_text:
        return False
    legacy_sections = extract_legacy_sections(html_text)
    if not legacy_sections:
        return False

    legacy_by_heading = {normalize_heading(h): (h, b) for h, b in legacy_sections}
    changed = False
    used_legacy: set[str] = set()

    for idx in range(1, 8):
        heading_key = f"section_{idx}_heading"
        body_key = f"section_{idx}_body"
        csv_heading = (row.get(heading_key) or "").strip()
        if not csv_heading:
            continue
        norm = normalize_heading(csv_heading)
        legacy = legacy_by_heading.get(norm)
        if not legacy:
            for ln, (lh, lb) in legacy_by_heading.items():
                if ln in used_legacy:
                    continue
                if norm in ln or ln in norm:
                    legacy = (lh, lb)
                    break
        if not legacy:
            continue
        _, body = legacy
        body = dedupe_repeated_phrases(body)
        used_legacy.add(normalize_heading(legacy[0]))
        if row.get(body_key) != body:
            row[body_key] = body
            changed = True

    # 空きスロットに legacy の未割当セクションを追加
    legacy_remaining = [
        (h, b)
        for h, b in legacy_sections
        if normalize_heading(h) not in used_legacy
    ]
    for h, b in legacy_remaining:
        placed = False
        for idx in range(1, 8):
            heading_key = f"section_{idx}_heading"
            body_key = f"section_{idx}_body"
            if not (row.get(heading_key) or "").strip():
                row[heading_key] = h
                row[body_key] = dedupe_repeated_phrases(b)
                changed = True
                placed = True
                break
        if not placed:
            break
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--git-ref", default=DEFAULT_GIT_REF)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    with GUIDE_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())

    updated = 0
    for row in rows:
        if restore_row(row, args.git_ref):
            updated += 1

    print(f"restored section bodies: {updated}/{len(rows)} articles")
    if args.dry_run:
        return 0

    tmp = GUIDE_CSV.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    shutil.move(str(tmp), str(GUIDE_CSV))
    print(f"Updated {GUIDE_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
