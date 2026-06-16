#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通常ガイドへ比較記事導線（related_links + 本文1文）をバッチ適用。"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_batch(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("affiliate_funnel_batch", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "FUNNEL_PATCHES"):
        raise ValueError(f"{path} must define FUNNEL_PATCHES dict")
    return mod


def _split_related(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(";") if x.strip()]


def _append_related(value: str, token: str) -> str:
    parts = _split_related(value)
    slug = token.split(":", 1)[0]
    if any(p.split(":", 1)[0] == slug for p in parts):
        return ";".join(parts)
    parts.append(token)
    return ";".join(parts)


def _append_body(body: str, sentence: str, *, slug_marker: str) -> str:
    if slug_marker and slug_marker in (body or ""):
        return body
    text = (body or "").rstrip()
    if not text:
        return sentence
    if not text.endswith("。"):
        text += "。"
    return text + sentence


def apply_patches(csv_path: Path, patches: dict, *, dry_run: bool = False) -> int:
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8-sig")))
    if not rows:
        return 0
    fieldnames = list(rows[0].keys())
    by_slug = {r["slug"]: r for r in rows}
    changed = 0

    for slug, patch in patches.items():
        row = by_slug.get(slug)
        if not row or (row.get("content_status") or "").strip() != "published":
            print(f"skip {slug}: missing or not published")
            continue

        updated = False
        for token in patch.get("related_links_append", []):
            new_rl = _append_related(row.get("related_links", ""), token)
            if new_rl != row.get("related_links", ""):
                row["related_links"] = new_rl
                updated = True

        for sec_key, sentence in patch.get("section_body_sentences", {}).items():
            old = row.get(sec_key, "")
            marker = patch.get("slug_markers", {}).get(sec_key, "")
            if not marker:
                for token in sentence.replace("、", " ").replace("。", " ").split():
                    if token.startswith("affiliate-"):
                        marker = token
                        break
            new = _append_body(old, sentence, slug_marker=marker)
            if new != old:
                row[sec_key] = new
                updated = True

        if updated:
            changed += 1
            print(f"patched {slug}")

    if changed and not dry_run:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", type=Path, help="FUNNEL_PATCHES を定義した batch py")
    parser.add_argument(
        "--csv",
        type=Path,
        default=ROOT / "data" / "guide_articles.csv",
        help="guide_articles.csv path",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    mod = load_batch(args.batch.resolve())
    n = apply_patches(args.csv, mod.FUNNEL_PATCHES, dry_run=args.dry_run)
    print(f"updated {n} row(s)")


if __name__ == "__main__":
    main()
