#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rewrite 正本の lead を管理体制記事基準（~220字）に短縮。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.editorial_quality import norm  # noqa: E402
from tools.fix_rewrite_reader_prose import EXAM_BLOCK_RE  # noqa: E402
from tools.guide_date_prose import is_schedule_heavy_slug, soften_dates_for_column  # noqa: E402
from tools.rewrite_module_io import discover_rewrite_files, load_rewrites_module, write_rewrite_module  # noqa: E402

OFFICIAL_TAIL_RE = re.compile(
    r"(?:公式情報は|数値·日程の公式情報は|条文·数値は|正本は)[^。]*?要項です[。]?"
)
LEAD_URL_TAIL_RE = re.compile(r"[^。]*(?:https?://|最新案内)[^。]+[。]?")
CROSSREF_SENTENCE_RE = re.compile(
    r"[^。]*(?:記事|ハブ)[^。]*(?:あわせて読んでください|をあわせて読んでください|を確認してください)[。]?"
)
SPECIALIZE_RE = re.compile(
    r"本記事(?:は|では)[^。]+?"
    r"(?:特化(?:しています|します)|説明(?:します|しています)|"
    r"整理(?:します|しています)|役割分担(?:しています|しています))[。]?"
)
EXAMPLE_SENTENCE_RE = re.compile(
    r"[^。]*(?:例えば|たとえば|次の一手：|次の一手:)[^。]+[。]?"
)
TRANSFER_EXAMPLE_RE = re.compile(
    r"[^。]*転記[^。]*解き直[^。]+[。]?"
)
NOTE_RE = re.compile(r"（(?:条文·規則|要項)[^）]*再確認）")


def _target_len(slug: str) -> int:
    return 300 if is_schedule_heavy_slug(slug) else 220


def _compress_example_dates(text: str) -> str:
    """例示内の2つ目以降の具体日を相対表現へ。"""
    out = text

    def _second_date(m: re.Match[str]) -> str:
        tail = m.group(3).lstrip("に")
        return m.group(1) + m.group(2) + "1週間後に" + tail

    out = re.sub(
        r"(\d{1,2}月\d{1,2}日(?:（[日月火水木金土]）)?|\d{1,2}/\d{1,2}(?:（[日月火水木金土]）)?)"
        r"([^。]{0,100}?)"
        r"(?:\d{1,2}月\d{1,2}日(?:（[日月火水木金土]）)?|\d{1,2}/\d{1,2}(?:（[日月火水木金土]）)?)"
        r"([^。]{0,48}?解き直)",
        _second_date,
        out,
        count=1,
    )
    return out


def _extract_example(text: str) -> str:
    m = EXAMPLE_SENTENCE_RE.search(text) or TRANSFER_EXAMPLE_RE.search(text)
    if not m:
        return ""
    ex = m.group(0).strip()
    ex = ex.replace("次の一手：", "例えば").replace("次の一手:", "例えば")
    if not ex.startswith(("例えば", "たとえば")):
        ex = "例えば" + ex.lstrip("。")
    ex = re.sub(r"「[^」]{28,}」", "「受験→合格→免許→選任」の流れ", ex)
    ex = re.sub(r"の流れの流れ", "の流れ", ex)
    ex = re.sub(r"流れのカレンダー", "流れ", ex)
    ex = _compress_example_dates(ex)
    return ex


def shorten_lead(lead: str, slug: str) -> str:
    raw = norm(lead)
    if not raw:
        return raw
    if len(raw) <= _target_len(slug):
        return raw

    out = OFFICIAL_TAIL_RE.sub("", raw)
    if not is_schedule_heavy_slug(slug):
        out = EXAM_BLOCK_RE.sub("", out)
        out = re.sub(
            r"試験は30問·300点·180点[^。]+8,800円(?:です)?[。]?",
            "",
            out,
        )
        out = re.sub(
            r"合格は30問·300点·180点[^。]+8,800円(?:です)?[。]?",
            "",
            out,
        )
        out = re.sub(
            r"30問·300点·180点[^。]+8,800円(?:です)?[。]?",
            "",
            out,
        )

    specialize = SPECIALIZE_RE.search(out)
    example = _extract_example(out)

    if specialize:
        topic_end = specialize.start()
        topic = out[:topic_end].strip()
        first = re.match(r"^[^。]+[。]", topic)
        if first and topic.count("。") > 1:
            topic = first.group(0)
        spec = specialize.group(0).strip()
        if not spec.endswith("。"):
            spec += "。"
        parts = [topic, spec, "詳細は各関連記事を参照してください。"]
        if example:
            parts.append(example)
        out = "".join(parts)
    else:
        first = re.match(r"^[^。]+[。]", out)
        topic = first.group(0) if first else out
        parts = [topic.strip(), "詳細は各関連記事を参照してください。"]
        if example:
            parts.append(example)
        out = "".join(parts)

    out = soften_dates_for_column(out, slug=slug, col="lead")
    out = _compress_example_dates(out)
    out = re.sub(r"(?<=[。])詳細は各関連記事を参照してください。詳細は各関連記事を参照してください。", "詳細は各関連記事を参照してください。", out)
    out = re.sub(r"[ \t·]{2,}", "·", out)
    out = re.sub(r"。{2,}", "。", out)
    out = out.strip()
    if out and not out.endswith("。"):
        out += "。"

    # まだ長い場合：例示文を短く（または汎用例示へ差し替え）
    if len(out) > _target_len(slug) + 20:
        generic_ex = "例えば日曜の演習で誤答した論点は本記事の表を転記し、1週間後に解き直してください。"
        if re.search(r"例えば|たとえば", out):
            out = re.sub(r"[^。]*(?:例えば|たとえば)[^。]+[。]", generic_ex, out, count=1)
        elif example:
            out = out.rstrip("。") + "。" + generic_ex
        else:
            out = out.rstrip("。") + "。" + generic_ex

    if len(out) > _target_len(slug) + 40 and example:
        short_ex = re.sub(
            r"(例えば|たとえば)[^。]+",
            r"\1演習で誤答した論点は本記事の表を転記し、1週間後に解き直してください",
            out,
            count=1,
        )
        if 80 <= len(short_ex) <= len(out):
            out = short_ex

    # 例示が無い場合は1文追加
    if not re.search(r"例えば|たとえば", out):
        out = (
            out.rstrip("。")
            + "。例えば日曜の演習で誤答した論点は本記事の表を転記し、1週間後に解き直してください。"
        )

    if NOTE_RE.search(out) and out.count("再確認") > 1:
        seen = False

        def _one_note(m: re.Match[str]) -> str:
            nonlocal seen
            if seen:
                return ""
            seen = True
            return m.group(0)

        out = NOTE_RE.sub(_one_note, out)

    out = LEAD_URL_TAIL_RE.sub("", out)
    out = re.sub(r"。{2,}", "。", out).strip()
    if out and not out.endswith("。"):
        out += "。"

    return out.strip()


def shorten_file(path: Path, *, dry_run: bool = False) -> tuple[bool, int, int]:
    mod = load_rewrites_module(path)
    rewrites = getattr(mod, "REWRITES")
    slug = next(iter(rewrites))
    patch = dict(rewrites[slug])
    before = patch.get("lead", "")
    after = shorten_lead(before, slug)
    if after == before:
        return False, len(before), len(after)
    patch["lead"] = after
    if not dry_run:
        write_rewrite_module(path, slug, {slug: patch})
    return True, len(before), len(after)


def main() -> int:
    ap = argparse.ArgumentParser(description="rewrite lead 短縮")
    ap.add_argument("--rewrites-dir", type=Path, default=ROOT / "tools" / "rewrites")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    changed = 0
    lengths: list[int] = []
    for path in discover_rewrite_files(args.rewrites_dir.resolve()):
        ok, _before, after = shorten_file(path, dry_run=args.dry_run)
        lengths.append(after)
        if ok:
            changed += 1
    print(
        f"shorten_rewrite_leads: changed={changed} "
        f"avg_len={sum(lengths) // max(len(lengths), 1)} "
        f"max_len={max(lengths) if lengths else 0} dry_run={args.dry_run}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
