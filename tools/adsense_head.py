# -*- coding: utf-8 -*-
"""Google AdSense の <head> 用スクリプト注入。

site-config.json の adsenseClientId があるときだけ出力する。
全公開 HTML の </head> 直前に置き、AdSense 審査・配信の共通タグとする。
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from tools.site_config import adsense_client_id

ADSENSE_MARKER_START = "<!--ADSENSE_HEAD-->"
ADSENSE_MARKER_END = "<!--/ADSENSE_HEAD-->"

_ADSENSE_BLOCK_RE = re.compile(
    rf"{re.escape(ADSENSE_MARKER_START)}[\s\S]*?{re.escape(ADSENSE_MARKER_END)}\n?",
    re.I,
)
_LEGACY_ADSENSE_SCRIPT_RE = re.compile(
    r'<script\b[^>]*\bsrc=["\']https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js\?client=[^"\']+["\'][^>]*>\s*</script>\s*',
    re.I,
)
_HEAD_CLOSE_RE = re.compile(r"</head>", re.I)


def _valid_client_id(raw: str) -> str:
    mid = (raw or "").strip()
    if re.fullmatch(r"ca-pub-\d+", mid):
        return mid
    return ""


def adsense_head_snippet() -> str:
    """生成 HTML の <head> 内用 AdSense タグ。未設定・不正 ID なら空文字。"""
    client = _valid_client_id(adsense_client_id())
    if not client:
        return ""
    esc = html.escape(client, quote=True)
    return (
        f"{ADSENSE_MARKER_START}\n"
        f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={esc}"\n'
        f'     crossorigin="anonymous"></script>\n'
        f"{ADSENSE_MARKER_END}"
    )


def inject_adsense_head(html_text: str) -> str:
    """HTML の <head> に AdSense スクリプトを冪等に挿入・更新する。"""
    client = _valid_client_id(adsense_client_id())
    if not client:
        cleaned = _ADSENSE_BLOCK_RE.sub("", html_text)
        return cleaned

    block = adsense_head_snippet()
    if not block:
        return html_text

    if ADSENSE_MARKER_START in html_text:
        return _ADSENSE_BLOCK_RE.sub(block + "\n", html_text, count=1)

    # マーカーなしの旧手書きタグを除去してから挿入
    html_text = _LEGACY_ADSENSE_SCRIPT_RE.sub("", html_text)
    if not _HEAD_CLOSE_RE.search(html_text):
        return html_text
    return _HEAD_CLOSE_RE.sub(block + "\n</head>", html_text, count=1)


def iter_public_html_files(root: Path) -> list[Path]:
    skip_parts = {".git", "public_site", "node_modules", ".cursor"}
    out: list[Path] = []
    for path in sorted(root.rglob("*.html")):
        if any(part in skip_parts for part in path.parts):
            continue
        out.append(path)
    return out


def patch_all_html(root: Path) -> tuple[int, int]:
    """全公開 HTML に inject。戻り値は (変更数, 対象数)。"""
    changed = 0
    paths = iter_public_html_files(root)
    for path in paths:
        old = path.read_text(encoding="utf-8")
        new = inject_adsense_head(old)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed += 1
    return changed, len(paths)
