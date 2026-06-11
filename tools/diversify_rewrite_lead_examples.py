#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rewrite lead の汎用例示を、正本内の user_intent·本文から記事別例示へ差し替え。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.editorial_quality import norm  # noqa: E402
from tools.guide_date_prose import CALENDAR_DATE_RE, soften_dates_for_column  # noqa: E402
from tools.rewrite_module_io import discover_rewrite_files, load_rewrites_module, write_rewrite_module  # noqa: E402
from tools.shorten_rewrite_leads import (  # noqa: E402
    EXAMPLE_SENTENCE_RE,
    TRANSFER_EXAMPLE_RE,
    _compress_example_dates,
)

CROSSREF = "詳細は各関連記事を参照してください。"
GENERIC_EXAMPLE_RES = (
    re.compile(
        r"例えば(?:日曜の)?演習で誤答した論点は本記事の表を転記し、1週間後に解き直してください。"
    ),
    re.compile(
        r"たとえば(?:日曜の)?演習で誤答した論点は本記事の表を転記し、1週間後に解き直してください。"
    ),
)
USER_INTENT_EXAMPLE_RE = re.compile(r"(?:たとえば|例えば)[^。]+")
MAX_EXAMPLE_LEN = 88


def _example_is_usable(ex: str) -> bool:
    if not ex or is_generic_example(ex):
        return False
    if not ex.startswith(("例えば", "たとえば")):
        return False
    if re.search(r"例えば(?:1週間後|次の演習日)に同論点", ex):
        return False
    if "本記事を読むと" in ex:
        return False
    if len(ex) < 28 or len(ex) > MAX_EXAMPLE_LEN + 6:
        return False
    if re.search(r"(?:なら|したら|場合)を本記事", ex):
        return False
    if re.search(r"(?:にから|しを本記事|誤答を本記事|たが.{1,3}を本記事|をセットしを|点·.{1,2}を本記事)", ex):
        return False
    if "解き直" not in ex and "1週間後" not in ex:
        return False
    return True


def _score_example(ex: str) -> int:
    score = 50
    if CALENDAR_DATE_RE.search(ex):
        score += 15
    if "解き直" in ex:
        score += 10
    if "表" in ex or "チェック" in ex:
        score += 5
    score -= abs(len(ex) - 72)
    return score


def _compact_example(raw: str) -> str:
    out = _normalize_example(raw)
    if len(out) <= MAX_EXAMPLE_LEN:
        return out

    body = re.sub(r"^例えば|^たとえば", "", out.rstrip("。"))
    date_m = CALENDAR_DATE_RE.search(body)
    if date_m:
        d = date_m.group(0)
        tail = body[date_m.end() :].lstrip("にの、 ")
        topic = tail.split("、")[0].split("。")[0][:22]
        topic = re.sub(r"(?:なら|したら|場合|とき|点|回|超|から)$", "", topic).rstrip("をにはがでと")
        if len(topic) < 4 or re.search(r"(?:解き|関$|が$|を$|に$|から$|て$|し$)", topic):
            topic = ""
        if topic:
            return f"例えば{d}に{topic}を本記事の表で確認し、1週間後に解き直してください。"
        return f"例えば{d}の前に本記事の表を転記し、1週間後に同論点を解き直してください。"

    clause = body.split("、")[0][:26].rstrip("をにはがでと")
    return f"例えば{clause}を表で整理し、1週間後に演習で解き直してください。"


def _finalize_example(raw: str, slug: str) -> str:
    ex = _compact_example(raw)
    softened = _compress_example_dates(soften_dates_for_column(ex, slug=slug, col="lead"))
    if _example_is_usable(softened):
        return softened
    if _example_is_usable(ex):
        return ex
    return ex


def _trim_example(ex: str, *, max_len: int = MAX_EXAMPLE_LEN) -> str:
    return _compact_example(ex) if len(ex) > max_len else _normalize_example(ex)
SOURCE_COLUMNS = (
    *(f"section_{n}_body" for n in range(1, 6)),
    "user_intent",
    *(f"faq_{n}_answer" for n in range(1, 4)),
)
USER_INTENT_BOILER_RE = re.compile(r"^本記事を読むと[、,]?")


def is_generic_example(text: str) -> bool:
    t = norm(text)
    return any(p.search(t) for p in GENERIC_EXAMPLE_RES)


def _strip_tables(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            continue
        lines.append(line)
    return " ".join(lines)


def _normalize_example(raw: str) -> str:
    ex = norm(raw).strip()
    ex = USER_INTENT_BOILER_RE.sub("", ex)
    ex = ex.replace("次の一手：", "例えば").replace("次の一手:", "例えば")
    ex = re.sub(r"^(?:たとえば|例えば)[、,]?", "", ex)
    ex = re.sub(r"^(?:たとえば|例えば)[、,]?", "", ex)
    if not ex.startswith(("例えば", "たとえば")):
        ex = "例えば" + ex.lstrip("、。")
    ex = re.sub(r"「[^」]{28,}」", "「受験→合格→免許→選任」の流れ", ex)
    ex = re.sub(r"の流れの流れ", "の流れ", ex)
    ex = re.sub(r"流れのカレンダー", "流れ", ex)
    ex = re.sub(r"1週間後にに", "1週間後に", ex)
    ex = re.sub(r"[ \t·]{2,}", "·", ex)
    if not ex.endswith("。"):
        ex += "。"
    return ex


def _extract_from_text(text: str) -> str:
    plain = _strip_tables(text)
    for pat in (EXAMPLE_SENTENCE_RE, TRANSFER_EXAMPLE_RE):
        for m in pat.finditer(plain):
            cand = m.group(0)
            if "本記事を読むと" in cand and len(cand) > 48:
                continue
            return cand
    m = USER_INTENT_EXAMPLE_RE.search(plain)
    if m:
        return m.group(0)
    return ""


def build_lead_example(slug: str, patch: dict[str, str]) -> str:
    best = ""
    best_score = -1
    for col_index, col in enumerate(SOURCE_COLUMNS):
        raw = norm(patch.get(col))
        if not raw:
            continue
        found = _extract_from_text(raw)
        if not found or is_generic_example(found):
            continue
        ex = _finalize_example(found, slug)
        if not _example_is_usable(ex):
            continue
        score = _score_example(ex) - col_index * 8
        if "解き直" in ex:
            score += 25
        if "1週間後" in ex:
            score += 10
        if score > best_score:
            best_score = score
            best = ex
    if best:
        return best

    kp = (patch.get("key_points") or "").split(";")[0].strip()
    heading = norm(patch.get("section_1_heading") or "")[:22]
    if kp:
        raw = f"例えば{kp}を本記事の表に書き出し、1週間後に演習10問で確認してください。"
    elif heading:
        raw = f"例えば{heading}の表を10分転記し、1週間後に同論点を解き直してください。"
    else:
        raw = f"例えば{slug}の要点表を転記し、1週間後に演習で解き直してください。"
    return _finalize_example(raw, slug)


def replace_lead_example(lead: str, example: str) -> str:
    base = norm(lead)
    ex = _trim_example(example)
    base = re.sub(r"[^。]*(?:例えば|たとえば)[^。]+[。]", "", base).strip()
    if CROSSREF not in base:
        if base and not base.endswith("。"):
            base += "。"
        base += CROSSREF
    elif not base.endswith("。"):
        base += "。"
    return base + ex


def lead_needs_diversify(lead: str) -> bool:
    t = norm(lead)
    if not t:
        return False
    if len(t) > 230:
        return True
    m = re.search(r"[^。]*(?:例えば|たとえば)[^。]+[。]", t)
    if not m:
        return True
    ex = m.group(0)
    return not _example_is_usable(ex)


def diversify_lead(lead: str, slug: str, patch: dict[str, str], *, force: bool = False) -> str:
    if not force and not lead_needs_diversify(lead):
        return norm(lead)
    return replace_lead_example(lead, build_lead_example(slug, patch))


def diversify_file(path: Path, *, dry_run: bool = False, force: bool = False) -> tuple[bool, str, str]:
    mod = load_rewrites_module(path)
    rewrites = getattr(mod, "REWRITES")
    slug = next(iter(rewrites))
    patch = dict(rewrites[slug])
    before = patch.get("lead", "")
    after = diversify_lead(before, slug, patch, force=force)
    if after == before:
        return False, before, after
    patch["lead"] = after
    if not dry_run:
        write_rewrite_module(path, slug, {slug: patch})
    return True, before, after


def _dedupe_rewrite_examples(rewrites_dir: Path, *, dry_run: bool = False) -> int:
    """同一例示文の slug には section_1_heading を差し込んで一意化。"""
    seen: dict[str, str] = {}
    changed = 0
    for path in discover_rewrite_files(rewrites_dir.resolve()):
        mod = load_rewrites_module(path)
        slug = next(iter(mod.REWRITES))
        patch = dict(mod.REWRITES[slug])
        lead = norm(patch.get("lead", ""))
        m = re.search(r"[^。]*(?:例えば|たとえば)[^。]+[。]", lead)
        if not m:
            continue
        ex = m.group(0)
        if ex not in seen:
            seen[ex] = slug
            continue
        heading = norm(patch.get("section_1_heading") or "")[:16]
        if not heading:
            continue
        alt = re.sub(r"^例えば", f"例えば{heading}の表で、", ex, count=1)
        if alt == ex or not _example_is_usable(alt) or len(alt) > MAX_EXAMPLE_LEN + 6:
            continue
        new_lead = replace_lead_example(lead, alt)
        if new_lead == lead:
            continue
        patch["lead"] = new_lead
        if not dry_run:
            write_rewrite_module(path, slug, {slug: patch})
        changed += 1
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description="rewrite lead 例示の記事別差し替え")
    ap.add_argument("--rewrites-dir", type=Path, default=ROOT / "tools" / "rewrites")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--slug", help="単体 slug のみ")
    ap.add_argument("--force", action="store_true", help="例示が有効でも再生成")
    args = ap.parse_args()

    changed = 0
    examples: list[str] = []
    for path in discover_rewrite_files(args.rewrites_dir.resolve()):
        slug = next(iter(load_rewrites_module(path).REWRITES))
        if args.slug and slug != args.slug:
            continue
        ok, _before, after = diversify_file(path, dry_run=args.dry_run, force=args.force)
        m = re.search(r"[^。]*(?:例えば|たとえば)[^。]+[。]", after)
        if m:
            examples.append(m.group(0))
        if ok:
            changed += 1

    deduped = _dedupe_rewrite_examples(args.rewrites_dir.resolve(), dry_run=args.dry_run)
    if deduped:
        print(f"dedupe_rewrite_lead_examples: changed={deduped}")

    from collections import Counter

    dup = sum(1 for c in Counter(examples).values() if c > 1)
    generic = sum(1 for ex in examples if is_generic_example(ex))
    print(
        f"diversify_rewrite_lead_examples: changed={changed} "
        f"generic_left={generic} duplicate_examples={dup} dry_run={args.dry_run}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
