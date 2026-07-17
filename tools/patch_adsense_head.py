#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全公開 HTML の <head> に AdSense スクリプトを注入する。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adsense_head import patch_all_html  # noqa: E402
from tools.site_config import adsense_client_id  # noqa: E402


def main() -> int:
    client = (adsense_client_id() or "").strip()
    if not client:
        print("patch_adsense_head: adsenseClientId 未設定のためスキップ")
        return 0
    changed, total = patch_all_html(ROOT)
    print(f"patch_adsense_head: updated {changed}/{total} HTML (client={client})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
