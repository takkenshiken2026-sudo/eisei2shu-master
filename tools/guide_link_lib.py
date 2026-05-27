"""試験ガイド記事本文の内部リンク変換。"""
from __future__ import annotations

import html
import re

MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def linkify_inline(text: str) -> str:
    """[ラベル](href) を <a> に変換し、それ以外はエスケープする。"""
    text = text or ""
    if not text:
        return ""
    parts: list[str] = []
    last = 0
    for match in MARKDOWN_LINK_RE.finditer(text):
        before = text[last : match.start()]
        if before:
            parts.append(html.escape(before))
        label, href = match.group(1), match.group(2).strip()
        if href.startswith(("http://", "https://", "mailto:")):
            rel = ' rel="noopener noreferrer"'
            target = ' target="_blank"'
        else:
            rel = ""
            target = ""
        parts.append(
            f'<a href="{html.escape(href, quote=True)}"{target}{rel}>'
            f"{html.escape(label)}</a>"
        )
        last = match.end()
    tail = text[last:]
    if tail:
        parts.append(html.escape(tail))
    return "".join(parts) if parts else html.escape(text)


def resolve_legacy_href(href: str) -> str:
    """旧 flat HTML の絶対・ルート相対パスを、記事 index.html からの相対パスへ。"""
    href = (href or "").strip()
    if not href or href.startswith(("http://", "https://", "mailto:")):
        return href
    if href in ("/", "/index.html"):
        return "../../index.html"
    if href.startswith("/articles/"):
        slug = href.removeprefix("/articles/").removesuffix(".html").strip("/")
        return f"../{slug}/"
    if href.startswith("/terms"):
        slug = href.removeprefix("/terms").strip("/").removesuffix(".html")
        if not slug or slug == "index":
            return "../../terms/index.html"
        return f"../../terms/{slug}.html"
    if href.startswith("#"):
        return href
    return href
