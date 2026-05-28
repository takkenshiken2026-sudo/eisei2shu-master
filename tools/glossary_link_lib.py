"""用語名から試験ガイド記事向けの内部リンクを生成する。"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from tools.build_glossary_pages import lookup_key
from tools.guide_link_lib import MARKDOWN_LINK_RE

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY_CSV = ROOT / "data" / "glossary_terms.csv"

# 記事一覧の表記ゆれ → 登録用語名
GUIDE_TERM_ALIASES: dict[str, str] = {
    "A測定・B測定": "A測定・B測定・C測定",
    "安全衛生委員会": "衛生委員会",
    "許容濃度": "許容濃度・管理濃度",
    "保護具": "個人用保護具",
    "全面換気": "全面換気・希釈換気",
    "SDS": "SDS（安全データシート）",
    "有機溶剤": "有機溶剤の脂溶性と中枢神経症状",
    "確定的影響": "確定的影響と確率的影響",
    "確率的影響": "確定的影響と確率的影響",
}


def norm(value: str | None) -> str:
    return (value or "").strip()


def load_glossary_entries() -> list[dict]:
    if not GLOSSARY_CSV.is_file():
        return []
    rows = list(csv.DictReader(GLOSSARY_CSV.read_text(encoding="utf-8-sig").splitlines()))
    used_slugs: dict[str, str] = {}
    entries: list[dict] = []
    for row in rows:
        term = norm(row.get("term"))
        if not term:
            continue
        legacy_slug = norm(row.get("slug")) or norm(row.get("url_slug"))
        if legacy_slug:
            slug_file = f"{legacy_slug}.html"
        else:
            continue
        if slug_file in used_slugs:
            continue
        used_slugs[slug_file] = term
        entries.append({"term": term, "slug_file": slug_file, "category": norm(row.get("category"))})
    return entries


def article_term_lookup(entries: list[dict] | None = None) -> dict[str, str]:
    """用語ラベル → articles/*/index.html からの相対 href（正式名称のみ）。"""
    entries = entries if entries is not None else load_glossary_entries()
    lookup: dict[str, str] = {}
    for e in entries:
        term = e["term"]
        href = f"../../terms/{e['slug_file']}"
        lookup[term] = href
        lookup[lookup_key(term)] = href
    for alias, target in GUIDE_TERM_ALIASES.items():
        href = lookup.get(target) or lookup.get(lookup_key(target))
        if href:
            lookup[alias] = href
            lookup[lookup_key(alias)] = href
    return lookup


def _sorted_term_keys(lookup: dict[str, str]) -> list[str]:
    # 短い別名キーによる誤リンク（例：「職場」）を避けるため、正式名称のみ使う
    names = {e["term"] for e in load_glossary_entries()} | set(GUIDE_TERM_ALIASES)
    keys = [k for k in lookup if k in names or k in GUIDE_TERM_ALIASES]
    return sorted(keys, key=len, reverse=True)


def _linkify_plain_segment(segment: str, lookup: dict[str, str], keys: list[str]) -> str:
    if not segment or not lookup:
        return segment
    pattern = re.compile("|".join(re.escape(k) for k in keys if k))
    out: list[str] = []
    pos = 0
    for match in pattern.finditer(segment):
        before = segment[pos : match.start()]
        if before:
            out.append(before)
        label = match.group(0)
        href = lookup.get(label) or lookup.get(lookup_key(label))
        if href:
            out.append(f"[{label}]({href})")
        else:
            out.append(label)
        pos = match.end()
    tail = segment[pos:]
    if tail:
        out.append(tail)
    return "".join(out) if out else segment


def linkify_glossary_terms(text: str, lookup: dict[str, str] | None = None) -> str:
    """プレーンテキスト中の登録用語を [用語](../../terms/…) 形式にする。"""
    text = text or ""
    if not text.strip():
        return text
    lookup = lookup if lookup is not None else article_term_lookup()
    if not lookup:
        return text
    keys = _sorted_term_keys(lookup)

    # 行全体が用語名のときは確実にリンク化（カテゴリ一覧向け）
    lines = text.split("\n")
    if len(lines) >= 2:
        linked_lines: list[str] = []
        changed = False
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("→") or stripped.startswith("**"):
                linked_lines.append(line)
                continue
            href = lookup.get(stripped) or lookup.get(lookup_key(stripped))
            if href and "[" not in stripped:
                linked_lines.append(f"[{stripped}]({href})")
                changed = True
            else:
                linked_lines.append(line)
        if changed:
            text = "\n".join(linked_lines)

    parts: list[str] = []
    last = 0
    for match in MARKDOWN_LINK_RE.finditer(text):
        before = text[last : match.start()]
        if before:
            parts.append(_linkify_plain_segment(before, lookup, keys))
        parts.append(match.group(0))
        last = match.end()
    tail = text[last:]
    if tail:
        parts.append(_linkify_plain_segment(tail, lookup, keys))
    return "".join(parts) if parts else _linkify_plain_segment(text, lookup, keys)


def term_name_to_markdown_link(name: str, lookup: dict[str, str] | None = None) -> str:
    """単一用語名をマークダウンリンクに（未登録はそのまま）。"""
    name = norm(name)
    if not name:
        return ""
    lookup = lookup if lookup is not None else article_term_lookup()
    resolved = GUIDE_TERM_ALIASES.get(name, name)
    href = lookup.get(resolved) or lookup.get(name) or lookup.get(lookup_key(resolved))
    if href:
        return f"[{name}]({href})"
    return name
