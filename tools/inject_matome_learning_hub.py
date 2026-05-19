#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""科目まとめ記事に学習導線（三角リンク）ブロックを挿入する。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from render_learning_hub import render_matome_learning_hub

MATOME_FILES = {
    "kankei-horei-matome.html": "law",
    "rodo-eisei-matome.html": "rights",
    "rodo-seiri-matome.html": "limit",
}

MARKER = 'id="matome-learning-hub"'


def inject(path: Path, field: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    hub = render_matome_learning_hub(path.name, field)
    pattern = re.compile(
        r"<p>→ .*?</p>\s*(?=</article>)",
        re.DOTALL,
    )
    if not pattern.search(text):
        print(f"  スキップ（置換対象なし）: {path.name}")
        return False
    new_text = pattern.sub(hub + "\n", text, count=1)
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    articles = repo / "articles"
    n = 0
    for filename, field in MATOME_FILES.items():
        p = articles / filename
        if not p.is_file():
            print(f"  見つかりません: {p}")
            continue
        if inject(p, field):
            print(f"  更新: {filename}")
            n += 1
    print(f"完了: {n} ファイル")


if __name__ == "__main__":
    main()
