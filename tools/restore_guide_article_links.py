#!/usr/bin/env python3
"""旧 articles/*.html から本文リンクを復元し、guide_articles.csv に反映する。"""
from __future__ import annotations

import argparse
import csv
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

ARROW_FIXES: dict[str, tuple[str, str]] = {
    "3kagetsu-goukaku": ("→ 6ヶ月プランはこちら", "→ [6ヶ月プランはこちら](../6kagetsu-keikaku/)"),
    "category-kankeihorei": (
        "→ 全用語解説一覧（267本）はこちら",
        "→ [全用語解説一覧（267本）はこちら](../../terms/index.html)",
    ),
    "category-rodoeisei": (
        "→ 全用語解説一覧（267本）はこちら",
        "→ [全用語解説一覧（267本）はこちら](../../terms/index.html)",
    ),
    "category-rodoseiri": (
        "→ 全用語解説一覧（267本）はこちら",
        "→ [全用語解説一覧（267本）はこちら](../../terms/index.html)",
    ),
}


def extract_body_links(html: str) -> list[tuple[str, str]]:
    start = html.find('class="article-body"')
    if start < 0:
        return []
    body = html[start : html.find("</article>", start)]
    return re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>', body)


def inject_link(row: dict[str, str], label: str, resolved: str) -> bool:
    md = f"[{label}]({resolved})"
    for i in range(1, 8):
        key = f"section_{i}_body"
        body = row.get(key) or ""
        if label in body and md not in body:
            new = body.replace(f"→ {label}", f"→ {md}").replace(label, md, 1)
            if new != body:
                row[key] = new
                return True
    for i in range(7, 0, -1):
        key = f"section_{i}_body"
        if (row.get(f"section_{i}_heading") or "").strip() and (row.get(key) or "").strip():
            row[key] = (row[key].rstrip() + f"\n\n→ {md}").strip()
            return True
    return False


def normalize_csv_hrefs(text: str) -> str:
    text = text.replace("(https://eisei2shu-master.jp/)", "(../../index.html#past)")
    text = text.replace("(https://eisei2shu-master.jp/index.html)", "(../../index.html)")
    text = text.replace(
        "→ [お問い合わせフォーム](#)",
        "→ [お問い合わせフォーム](https://forms.gle/51E5d6D41BZETjhY6)",
    )
    text = text.replace("\n→ [Twitter/X](#)\n", "\n")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--git-ref", default=DEFAULT_GIT_REF)
    args = parser.parse_args()

    with GUIDE_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())

    by_slug = {r["slug"]: r for r in rows if r.get("slug")}
    stats = {"injected": 0, "missing_html": 0}

    for slug, row in by_slug.items():
        path = f"articles/{slug}.html"
        try:
            html = subprocess.check_output(
                ["git", "show", f"{args.git_ref}:{path}"],
                text=True,
                cwd=ROOT,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            stats["missing_html"] += 1
            continue
        for href, label in extract_body_links(html):
            label = label.strip()
            if not label or label == slug or re.fullmatch(r"[a-z0-9-]+", label):
                continue
            if inject_link(row, label, resolve_legacy_href(href)):
                stats["injected"] += 1

    for slug, (old, new) in ARROW_FIXES.items():
        row = by_slug.get(slug)
        if not row:
            continue
        for i in range(1, 8):
            key = f"section_{i}_body"
            if old in (row.get(key) or ""):
                row[key] = row[key].replace(old, new)
                stats["injected"] += 1

    for row in rows:
        for i in range(1, 8):
            key = f"section_{i}_body"
            if row.get(key):
                row[key] = normalize_csv_hrefs(row[key])

    tmp = GUIDE_CSV.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    shutil.move(str(tmp), str(GUIDE_CSV))
    print(f"restored link markers: {stats['injected']}, no legacy html: {stats['missing_html']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
