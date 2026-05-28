"""手作り用語データをスラッグで参照（import 専用）。"""
from __future__ import annotations

import importlib.util
from pathlib import Path

HANDMADE_DIR = Path(__file__).resolve().parents[1] / "handmade"


def load_handmade_by_slug() -> dict[str, dict]:
    out: dict[str, dict] = {}
    seen_lists: set[int] = set()
    for path in sorted(HANDMADE_DIR.glob("glossary_*_data.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(mod)
        for attr in dir(mod):
            if not attr.startswith("HANDMADE"):
                continue
            val = getattr(mod, attr)
            if not isinstance(val, list) or not val or not isinstance(val[0], dict):
                continue
            if id(val) in seen_lists:
                continue
            seen_lists.add(id(val))
            for item in val:
                slug = (item.get("slug") or "").strip()
                if slug:
                    out[slug] = item
    return out


def tips_from_handmade(item: dict | None) -> list[str]:
    if not item:
        return []
    tips: list[str] = []
    for _title, body in item.get("sections") or []:
        if _title == "試験で狙われる頻出ポイント" and isinstance(body, list):
            for row in body:
                if isinstance(row, str):
                    tips.append(row)
    return tips[:4]
