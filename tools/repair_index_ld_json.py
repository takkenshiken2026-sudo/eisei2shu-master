#!/usr/bin/env python3
"""誤って HTML コメント内へ入った JSON-LD を除去し、</html> 直前に正しく配置する。"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "index.html"


def git_head_text() -> str:
    return subprocess.check_output(
        ["git", "show", "HEAD:index.html"],
        cwd=ROOT,
        text=True,
    )


def extract_ld_blocks(html: str) -> list[str]:
    return re.findall(
        r'<script type="application/ld\+json">.*?</script>',
        html,
        flags=re.DOTALL,
    )


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    head_html = git_head_text()
    blocks = extract_ld_blocks(head_html)
    if len(blocks) != 2:
        raise SystemExit(f"HEAD から JSON-LD を2件取得できませんでした: {len(blocks)}")

    # コメント内の誤挿入ブロックを削除
    text = re.sub(
        r"<!-- REMOVED_LD_JSON -->.*?</script>\s*"
        r"</body> タグの直前に、このファイルの内容を\s*"
        r"まるごとコピー&ペーストしてください。\s*"
        r"既存コードは一切変更不要です。\s*"
        r"\s*── 動作要件 ──.*?========================================================================\s*-->\s*",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )

    # 重複したコメント断片（導入方法が2回ある場合）
    dup = re.search(
        r"(  ── 導入方法 ──\s*"
        r"index\.html の </body> タグの直前に、このファイルの内容を\s*"
        r"まるごとコピー&ペーストしてください。\s*"
        r"既存コードは一切変更不要です。\s*"
        r"\s*── 動作要件 ──.*?========================================================================\s*-->\s*){2}",
        text,
        flags=re.DOTALL,
    )
    if dup:
        text = text.replace(dup.group(0), dup.group(1), 1)

    footer = "\n".join(blocks) + "\n"
    if footer not in text:
        text = re.sub(r"</html>\s*$", footer + "</html>\n", text, count=1)

    # スクリプト defer
    text = text.replace(
        '<script src="eisei2-data-glossary.js"></script>',
        '<script defer src="eisei2-data-glossary.js"></script>',
    )
    text = text.replace(
        '<script>\n\n(function enrichGlossaryPlaceholderDesc',
        '<script defer>\n\n(function enrichGlossaryPlaceholderDesc',
        1,
    )

    TARGET.write_text(text, encoding="utf-8")
    print("repair_index_ld_json.py: OK")


if __name__ == "__main__":
    main()
