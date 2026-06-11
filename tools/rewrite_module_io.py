#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/rewrites/*.py の REWRITES 読み書き。"""

from __future__ import annotations

import importlib.util
import json
import re
from datetime import date
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]

# validate_guide_hand_batch と同じ列順
PATCH_KEY_ORDER = (
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


def load_rewrites_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"rewrite_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "REWRITES"):
        raise ValueError(f"{path} must define REWRITES dict")
    return mod


def _chunk_jp_string(text: str, width: int = 42) -> list[str]:
    if not text:
        return []
    parts: list[str] = []
    i = 0
    while i < len(text):
        end = min(i + width, len(text))
        if end < len(text):
            chunk = text[i:end]
            best = -1
            for sep in "。、·；":
                pos = chunk.rfind(sep)
                if pos > width // 3:
                    best = max(best, pos)
            if best >= 0:
                end = i + best + 1
        parts.append(text[i:end])
        i = end
    return parts


def _format_string_field(key: str, value: str, indent: str) -> list[str]:
    if "\n" in value:
        lines = [f'{indent}"{key}": (']
        for line in value.split("\n"):
            lines.append(f"{indent}    {json.dumps(line, ensure_ascii=False)}")
        lines.append(f"{indent}),")
        return lines
    chunks = _chunk_jp_string(value)
    if len(chunks) <= 1 and len(value) < 72:
        return [f'{indent}"{key}": {json.dumps(value, ensure_ascii=False)},']
    lines = [f'{indent}"{key}": (']
    for chunk in chunks:
        lines.append(f"{indent}    {json.dumps(chunk, ensure_ascii=False)}")
    lines.append(f"{indent}),")
    return lines


def emit_rewrite_module(slug: str, rewrites: dict[str, dict[str, str]], *, today: str | None = None) -> str:
    today = today or date.today().isoformat()
    if slug not in rewrites:
        raise ValueError(f"slug {slug} not in rewrites")
    patch = rewrites[slug]
    lines = [
        "#!/usr/bin/env python3",
        "# -*- coding: utf-8 -*-",
        f'"""二衛 guide 単体リライト: {slug}（{today}）。"""',
        "",
        "from __future__ import annotations",
        "",
        "REWRITES: dict[str, dict[str, str]] = {",
        f'    "{slug}": {{',
    ]
    seen: set[str] = set()
    for key in PATCH_KEY_ORDER:
        if key not in patch:
            continue
        val = patch[key]
        if not isinstance(val, str) or not val.strip():
            continue
        lines.extend(_format_string_field(key, val, "        "))
        seen.add(key)
    for key in sorted(patch.keys()):
        if key in seen:
            continue
        val = patch[key]
        if not isinstance(val, str):
            continue
        lines.extend(_format_string_field(key, val, "        "))
    lines.extend(["    },", "}", ""])
    return "\n".join(lines)


def write_rewrite_module(path: Path, slug: str, rewrites: dict[str, dict[str, str]]) -> None:
    path.write_text(emit_rewrite_module(slug, rewrites), encoding="utf-8")


def discover_rewrite_files(rewrites_dir: Path) -> list[Path]:
    return sorted(
        p for p in rewrites_dir.glob("*.py") if p.is_file() and p.name != "__init__.py"
    )
