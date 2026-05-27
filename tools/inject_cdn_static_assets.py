#!/usr/bin/env python3
"""
GitHub Pages 公開用 index.html の静的アセット URL を jsDelivr に差し替え（長期キャッシュ）。

環境変数 GITHUB_REPOSITORY, GITHUB_SHA が無い場合は何もしない。

例:
  TARGET=public_site/index.html GITHUB_REPOSITORY=owner/repo GITHUB_SHA=abc123 \\
    python3 tools/inject_cdn_static_assets.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ASSETS = (
    "eisei2-data-glossary.js",
    "eisei2-data-original.js",
    "eisei2-master-data.js",
    "site-theme.css",
    "site-app.css",
)


def main() -> None:
    target = Path(os.environ.get("TARGET", "public_site/index.html"))
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    sha = os.environ.get("GITHUB_SHA", "").strip()
    if not repo or not sha:
        print("inject_cdn_static_assets.py: GITHUB_REPOSITORY / GITHUB_SHA 未設定のためスキップ")
        return
    if not target.is_file():
        print(f"inject_cdn_static_assets.py: ファイルがありません: {target}", file=sys.stderr)
        sys.exit(1)

    base = f"https://cdn.jsdelivr.net/gh/{repo}@{sha}"
    text = target.read_text(encoding="utf-8")
    count = 0
    for name in ASSETS:
        url = f"{base}/{name}"
        for attr in ("src", "href"):
            pat = re.compile(rf'({attr}="){re.escape(name)}(")')
            text, n = pat.subn(rf"\1{url}\2", text)
            count += n
        # loadExamScriptOnce('eisei2-master-data.js') 等の JS 文字列
        pat_q = re.compile(rf"(['\"]){re.escape(name)}(['\"])")
        text, n = pat_q.subn(rf"\1{url}\2", text)
        count += n
        # EXAM_DATA_BUNDLES 配列
        pat_arr = re.compile(rf"(['\"]){re.escape(name)}(['\"])")
        # already counted by pat_q
    if count == 0:
        print(f"inject_cdn_static_assets.py: 置換 0 件 ({target})", file=sys.stderr)
        sys.exit(1)
    target.write_text(text, encoding="utf-8")
    print(f"inject_cdn_static_assets.py: {count} 件を {base}/... に差し替え ({target})")


if __name__ == "__main__":
    main()
