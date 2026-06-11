#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手書きリライト正本（tools/rewrites/*.py）の読者向け prose を一括修復。

テンプレ感（正本乱用·同一試験数値ブロック·「たとえば6月11日——」等）を
記事ごとに差別化し、shikaku-merit で確立したリード品質基準に寄せる。

  python3 tools/fix_rewrite_reader_prose.py --dry-run
  python3 tools/fix_rewrite_reader_prose.py
  python3 tools/fix_rewrite_reader_prose.py --only-slugs sennin-people,shutsudai-keiko
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.editorial_quality import norm  # noqa: E402
from tools.fix_guide_week_template_prose import (  # noqa: E402
    fix_action_item,
    fix_section_heading,
    fix_title,
    scrub_exam_prefixed_labels,
    shorten_md_links,
    slug_titles_from_rows,
    soften_seibon,
    strip_week_template_sentences,
)
from tools.rewrite_module_io import (  # noqa: E402
    discover_rewrite_files,
    load_rewrites_module,
    write_rewrite_module,
)

TEXT_COLS = (
    "title",
    "meta_description",
    "lead",
    "user_intent",
    "action_items",
    "key_points",
    *(f"section_{n}_heading" for n in range(1, 8)),
    *(f"section_{n}_body" for n in range(1, 8)),
    *(f"faq_{n}_question" for n in range(1, 5)),
    *(f"faq_{n}_answer" for n in range(1, 5)),
)

EXAM_BLOCK_RE = re.compile(
    r"30問·300点·180点（60%）·各科目40点以上·"
    r"3科目×各10問·有害業務除外·約3時間·"
    r"2026年度例10月11日（日）13:30開始·"
    r"受験料8,800円(?:です)?[。]?"
)

EXAM_LEAD_KEEP = frozenset(
    {
        "about",
        "exam-format-overview",
        "exam-overview",
        "goukaku-kijun",
        "goukakuritsu",
        "pass-score",
        "pass-rate",
        "pass-rate-how-to-read",
        "exam-difficulty",
        "juken-shikaku",
        "shiken-nittei",
        "exam-fees",
        "exam-schedule",
        "exam-eligibility",
        "exam-application-flow",
        "1shu-2shu-chigai",
        "exam-purpose-and-career",
        "subject-breakdown",
        "exam-scope-overview",
        "nankaisei",
        "nankaimo-ochiru",
        "ichimon-ittou",
        "shikaku-merit",
        "shikaku-merit-shokuba",
        "career-after-qualification",
    }
)

LEAD_DATE_OPENERS = (
    "学習例として、",
    "演習でつまずいたときは、",
    "定着確認の目安：",
    "復習ステップ：",
    "次の一手：",
    "実践メモ：",
    "週次の振り返り：",
)

TITLE_BRACKET_NOISE_RE = re.compile(r"【[^】]*(?:記事連携|正本|連携ルート)[^】]*】")


def _load_exam(root: Path) -> str:
    cfg = root / "site-config.json"
    if not cfg.is_file():
        return ""
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        return norm(data.get("examName") or "")
    except json.JSONDecodeError:
        return ""


def _load_official(root: Path) -> str:
    cfg = root / "site-config.json"
    if not cfg.is_file():
        return "公式情報"
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        return norm(data.get("officialOrganization") or "公式情報")
    except json.JSONDecodeError:
        return "公式情報"


def should_keep_exam_block(slug: str) -> bool:
    if slug in EXAM_LEAD_KEEP:
        return True
    return slug.startswith(("exam-", "pass-", "goukaku", "shiken-", "juken-"))


def fix_seibon_chains(text: str) -> str:
    out = text
    out = re.sub(
        r"本記事は(.+?)が正本、",
        r"本記事は\1に特化しています。",
        out,
        count=1,
    )
    out = re.sub(r"([^、。]+?)記事が正本です。", r"\1記事をあわせて読んでください。", out)
    out = re.sub(r"([^、。]+?)が正本、", r"\1は別記事で説明します。", out)
    out = re.sub(r"([^、。]+?)は正本、", r"\1は別記事で説明します。", out)
    out = re.sub(r"([^、。]+?)が正本です。", r"\1は別記事で説明します。", out)
    return out


def soften_seibon_extended(text: str) -> str:
    out = fix_seibon_chains(text)
    out = soften_seibon(out)
    out = re.sub(r"正本は労働", "条文·数値は労働", out)
    out = re.sub(r"正本は安全衛生", "条文·数値は安全衛生", out)
    out = re.sub(r"正本を確認", "公式情報を確認", out)
    return out


BROKEN_IMPERATIVE_FIXES: tuple[tuple[str, str], ...] = (
    ("解き直すてください", "解き直してください"),
    ("書き込むてください", "書き込んでください"),
    ("書き直すてください", "書き直してください"),
    ("外すてください", "外してください"),
    ("見直すてください", "見直してください"),
    ("進むてください", "進んでください"),
    ("開くてください", "開いてください"),
    ("出すてください", "出してください"),
    ("解くてください", "解いてください"),
    ("置くてください", "置いてください"),
    ("おくてください", "おいてください"),
    ("書くてください", "書いてください"),
)


def fix_broken_imperatives(text: str) -> str:
    out = text
    for old, new in BROKEN_IMPERATIVE_FIXES:
        out = out.replace(old, new)
    return out


def replace_teiban_sentences(text: str) -> str:
    known = (
        (r"解き直すのが定番です", "解き直してください"),
        (r"書き込むのが定番です", "書き込んでください"),
        (r"書き直すのが定番です", "書き直してください"),
        (r"外すのが定番です", "外してください"),
        (r"見直すのが定番です", "見直してください"),
        (r"進むのが定番です", "進んでください"),
        (r"開くのが定番です", "開いてください"),
        (r"出すのが定番です", "出してください"),
        (r"解くのが定番です", "解いてください"),
        (r"置くのが定番です", "置いてください"),
        (r"書くのが定番です", "書いてください"),
    )
    out = text
    for pat, repl in known:
        out = re.sub(pat, repl, out)
    out = re.sub(r"のが定番です\.?", "。", out)
    out = re.sub(r"が定番です\.?", "。", out)
    return out


def vary_lead_date_opener(text: str, slug: str) -> str:
    idx = sum(ord(c) for c in slug) % len(LEAD_DATE_OPENERS)
    opener = LEAD_DATE_OPENERS[idx]
    out = re.sub(r"たとえば6月11日——", opener, text)
    out = re.sub(r"たとえば6/\d+——", opener, out)
    out = re.sub(r"たとえば6月11日[、,——]", opener, out)
    return out


def trim_lead_exam_block(lead: str, slug: str) -> str:
    if should_keep_exam_block(slug):
        return lead
    out = EXAM_BLOCK_RE.sub("", lead)
    out = re.sub(r"試験は(?:です)?[。]?", "", out, count=1)
    return out


def fix_reader_title(title: str, exam: str) -> str:
    t = fix_title(title, exam)
    t = TITLE_BRACKET_NOISE_RE.sub("", t)
    return t.strip()


def humanize_lead(
    lead: str,
    slug: str,
    *,
    slug_titles: dict[str, str],
    exam: str,
) -> str:
    out = fix_seibon_chains(lead)
    out = replace_teiban_sentences(out)
    out = strip_week_template_sentences(out)
    out = trim_lead_exam_block(out, slug)
    out = vary_lead_date_opener(out, slug)
    out = soften_seibon(out)
    out = re.sub(r"正本は労働", "条文·数値は労働", out)
    out = re.sub(r"正本は安全衛生", "条文·数値は安全衛生", out)
    out = shorten_md_links(out, slug_titles, exam=exam)
    out = scrub_exam_prefixed_labels(out, exam, slug_titles)
    out = fix_broken_imperatives(out)
    out = re.sub(r"[ \t·]{2,}", "·", out)
    return out.strip()


def humanize_text(
    text: str,
    *,
    slug: str,
    col: str,
    slug_titles: dict[str, str],
    exam: str,
    official: str,
    section_num: int = 0,
    heading: str = "",
    topic: str = "",
) -> str:
    raw = norm(text)
    if not raw:
        return raw
    if col == "lead":
        return humanize_lead(raw, slug, slug_titles=slug_titles, exam=exam)
    if col == "action_items":
        parts = [
            fix_action_item(soften_seibon_extended(p))
            for p in re.split(r"[;；]", raw)
            if p.strip()
        ]
        return fix_broken_imperatives(";".join(p for p in parts if p))
    if col.endswith("_heading"):
        return fix_broken_imperatives(
            fix_section_heading(soften_seibon_extended(raw), section_num=section_num, exam=exam)
        )
    if col in {"meta_description", "user_intent", "key_points"}:
        out = soften_seibon_extended(raw)
        out = shorten_md_links(out, slug_titles, exam=exam)
        return fix_broken_imperatives(scrub_exam_prefixed_labels(out, exam, slug_titles).strip())
    # section_body / faq — 週次テンプレ strip しない（本文欠落防止）
    out = soften_seibon_extended(raw)
    out = shorten_md_links(out, slug_titles, exam=exam)
    return fix_broken_imperatives(scrub_exam_prefixed_labels(out, exam, slug_titles).strip())


def fix_rewrite_patch(
    slug: str,
    patch: dict[str, str],
    *,
    slug_titles: dict[str, str],
    exam: str,
    official: str,
) -> dict[str, str]:
    topic = patch.get("title", "") or slug
    out: dict[str, str] = {}
    for key, val in patch.items():
        if not isinstance(val, str):
            continue
        out[key] = val
    if out.get("title"):
        out["title"] = fix_reader_title(out["title"], exam)
    for col in TEXT_COLS:
        if col == "title" or col not in out or not out[col]:
            continue
        sec_num = 0
        heading = ""
        if col.startswith("section_") and "_body" in col:
            sec_num = int(col.split("_")[1])
            heading = norm(out.get(f"section_{sec_num}_heading"))
        elif col.startswith("section_") and "_heading" in col:
            sec_num = int(col.split("_")[1])
        out[col] = humanize_text(
            out[col],
            slug=slug,
            col=col,
            slug_titles=slug_titles,
            exam=exam,
            official=official,
            section_num=sec_num,
            heading=heading,
            topic=topic,
        )
    return out


def fix_all_rewrites(
    root: Path,
    *,
    rewrites_dir: Path,
    only_slugs: frozenset[str] | None = None,
    dry_run: bool = False,
) -> dict:
    guide_csv = root / "data" / "guide_articles.csv"
    slug_titles: dict[str, str] = {}
    if guide_csv.is_file():
        with guide_csv.open(encoding="utf-8-sig", newline="") as f:
            slug_titles = slug_titles_from_rows(list(csv.DictReader(f)))
    exam = _load_exam(root)
    official = _load_official(root)

    changed_files = 0
    changed_slugs = 0
    for path in discover_rewrite_files(rewrites_dir):
        mod = load_rewrites_module(path)
        rewrites: dict[str, dict[str, str]] = getattr(mod, "REWRITES")
        file_changed = False
        new_rewrites: dict[str, dict[str, str]] = {}
        for slug, patch in rewrites.items():
            if only_slugs is not None and slug not in only_slugs:
                new_rewrites[slug] = patch
                continue
            fixed = fix_rewrite_patch(
                slug, patch, slug_titles=slug_titles, exam=exam, official=official
            )
            if fixed != patch:
                changed_slugs += 1
                file_changed = True
            new_rewrites[slug] = fixed
        if file_changed:
            changed_files += 1
            if not dry_run:
                slug = next(iter(new_rewrites))
                write_rewrite_module(path, slug, new_rewrites)
    return {"changed_files": changed_files, "changed_slugs": changed_slugs, "dry_run": dry_run}


def main() -> int:
    ap = argparse.ArgumentParser(description="手書きリライト prose 一括修復")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--rewrites-dir", type=Path, default=ROOT / "tools" / "rewrites")
    ap.add_argument("--only-slugs", default="", help="カンマ区切り slug")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    only = frozenset(s.strip() for s in args.only_slugs.split(",") if s.strip()) or None
    stats = fix_all_rewrites(
        args.root.resolve(),
        rewrites_dir=args.rewrites_dir.resolve(),
        only_slugs=only,
        dry_run=args.dry_run,
    )
    print(f"fix rewrite reader prose: {stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
