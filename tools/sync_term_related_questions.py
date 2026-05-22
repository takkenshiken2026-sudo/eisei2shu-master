#!/usr/bin/env python3
"""term-question-links.json を用語記事 frontmatter の related_questions に反映。"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTICLES = REPO / "eisei-articles" / "articles"
LINKS_JSON = REPO / "docs" / "term-question-links.json"


def main() -> None:
    links = json.loads(LINKS_JSON.read_text(encoding="utf-8"))
    updated = 0
    for md in ARTICLES.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        fm = parts[1]
        m = re.search(r"^slug:\s*(\S+)\s*$", fm, re.MULTILINE)
        if not m:
            continue
        slug = m.group(1)
        items = links.get(slug)
        if not items:
            continue
        rows = []
        for item in items[:8]:
            qid = str(item.get("id", "")).strip()
            label = str(item.get("label", qid)).strip()
            if qid:
                rows.append(f"{qid}:{label}")
        value = ";".join(rows)
        if re.search(r"^related_questions:\s*", fm, re.MULTILINE):
            fm = re.sub(
                r"^related_questions:.*$",
                f"related_questions: {value}",
                fm,
                count=1,
                flags=re.MULTILINE,
            )
        else:
            fm = fm.rstrip() + f"\nrelated_questions: {value}\n"
        md.write_text("---" + fm + "---" + parts[2], encoding="utf-8")
        updated += 1
    print(f"synced related_questions: {updated} articles")


if __name__ == "__main__":
    main()
