#!/usr/bin/env python3
"""
index.html の巨大インライン <style> を site-app.css に切り出し、
初回描画用のクリティカル CSS のみ head に残す。

使い方:
  python3 tools/extract_site_app_css.py
  python3 tools/extract_site_app_css.py path/to/index.html
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "index.html"
DEFAULT_CSS = ROOT / "site-app.css"

STYLE_BLOCK_RE = re.compile(r"<style>\s*(.*?)\s*</style>\s*", re.DOTALL)

CRITICAL_CSS = """<style id="site-critical">
:root{--bg:#fff;--bg2:#fff;--bg3:#f4f4f5;--bg4:#e4e4e7;--border:rgba(0,0,0,.09);--border2:rgba(0,0,0,.2);--text:#111;--ink:#333;--sel:#333;--sel-s:#e8e8e8;--text2:#555;--text3:#999;--blue:#444;--blue-d:#333;--blue-s:#f0f0f0;--blue-b:rgba(0,0,0,.1);--red:#c0392b;--red-s:#fdf2f2;--red-b:rgba(192,57,43,.14);--green:#1a7a40;--grn-s:#f0fdf4;--grn-b:rgba(26,122,64,.14);--amber:#444;--amb-s:#f0f0f2;--font:system-ui,-apple-system,'Noto Sans JP',sans-serif;--mono:system-ui,-apple-system,'Noto Sans JP',sans-serif;--fs-title:24px;--fs-body:16px;--fs-sub:14px;--fs-caption:12px;--fs-tiny:10px;--fw-strong:700;--fw-normal:500;--fnav-h:56px;--r:6px;--r2:10px;--sh:0 1px 3px rgba(0,0,0,.07),0 1px 2px rgba(0,0,0,.04);--sh2:0 4px 16px rgba(0,0,0,.1);--sb:208px}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--font);font-size:var(--fs-body);background:#f0f0f1;color:var(--text);min-height:100vh;-webkit-font-smoothing:antialiased}
.main{background:#f0f0f1}
#app{display:block;min-height:100vh}
.topnav{position:sticky;top:0;z-index:30;background:#fff;border-bottom:1px solid var(--border)}
.topnav-inner{max-width:1080px;margin:0 auto;padding:0 20px;height:54px;display:flex;align-items:center;gap:0}
.topnav-logo{display:flex;align-items:center;gap:9px;text-decoration:none;color:var(--text);cursor:pointer;margin-right:28px;flex-shrink:0}
.topnav-logo-mark{width:28px;height:28px;border-radius:7px;background:var(--ink);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:var(--bg2);flex-shrink:0}
.topnav-logo-text{font-size:16px;font-weight:700;letter-spacing:-.01em;white-space:nowrap}
.topnav-logo-stack{display:flex;flex-direction:column;align-items:flex-start;gap:1px;line-height:1.15;min-width:0}
.topnav-logo-sub{font-size:10px;font-weight:600;color:var(--text3);line-height:1.25;white-space:normal;max-width:min(220px,52vw)}
.topnav-links{display:flex;align-items:center;gap:2px;flex:1}
.topnav-link{display:flex;align-items:center;gap:6px;padding:6px 12px;border-radius:var(--r);cursor:pointer;font-size:14px;color:var(--text2);border:none;background:none;font-family:var(--font);text-decoration:none}
.topnav-link.active{background:var(--bg3);color:var(--text);font-weight:600}
.topnav-login-btn,.topnav-logout-btn{margin-left:auto;padding:6px 14px;border-radius:var(--r);border:1px solid var(--border2);font-size:12px;font-weight:600;cursor:pointer;font-family:var(--font);white-space:nowrap;flex-shrink:0}
.topnav-login-btn{background:var(--ink);color:var(--bg2)}
.topnav-logout-btn{background:var(--bg2);color:var(--text2)}
.topnav-hamburger{display:none;margin-left:8px;width:36px;height:36px;border-radius:var(--r);border:1px solid var(--border2);background:var(--bg2);align-items:center;justify-content:center;cursor:pointer;flex-shrink:0}
.main{min-height:calc(100vh - 54px);padding-bottom:68px}
.page{display:none;padding:28px 20px;max-width:960px;margin:0 auto}
.page#page-quiz-start{max-width:1080px}
.page.active{background:#fff;min-height:calc(100vh - 54px - 40px);border-left:1px solid var(--border);border-right:1px solid var(--border);display:block}
.page-title{font-size:var(--fs-title);font-weight:var(--fw-strong);margin-bottom:6px;line-height:1.3}
.page-sub{font-size:var(--fs-sub);color:var(--text2);margin-bottom:22px;line-height:1.65}
.mode-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:24px}
.mode-card-v2{background:#fff;border:1.5px solid var(--border2);border-radius:var(--r2);padding:16px 20px;cursor:pointer;display:flex;align-items:center;gap:16px;box-shadow:var(--sh)}
.mode-num-v2{font-size:12px;font-family:var(--mono);color:var(--text3);flex-shrink:0;width:20px;text-align:center}
.mode-body-v2{flex:1;min-width:0}
.mode-purpose-v2{font-size:12px;color:var(--text2);font-weight:500;margin-bottom:3px}
.mode-title-v2{font-size:16px;font-weight:700;color:var(--text);line-height:1.3}
.mode-arrow-v2{color:var(--text3);font-size:16px;flex-shrink:0}
.mode-card-header{display:flex;align-items:center;gap:9px;margin-bottom:10px}
.mode-icon-wrap{width:30px;height:30px;border-radius:7px;background:#e8e8eb;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.mode-card-title{font-size:14px;font-weight:700;color:var(--text);line-height:1.2}
.mission-card{background:#fff;border:1.5px solid var(--border2);border-radius:var(--r2);padding:18px 20px;margin-bottom:12px;box-shadow:var(--sh)}
@media(max-width:700px){:root{--fs-title:18px;--fs-body:14px;--fs-sub:13px;--fnav-h:0px}.topnav-links{display:none}.topnav-hamburger{display:flex}.topnav-inner{padding:0 10px;height:52px}.main{min-height:calc(100vh - 52px);padding-bottom:0}.page{padding:14px 14px calc(96px + env(safe-area-inset-bottom))}.mode-grid{grid-template-columns:1fr 1fr;gap:8px}.mode-card-v2{padding:13px 14px;gap:10px;min-height:86px}.mode-purpose-v2,.mode-title-v2{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.mode-title-v2{font-size:17px}.mission-card{padding:14px 16px}}
</style>
<link rel="preload" href="site-app.css" as="style">
<link rel="stylesheet" href="site-app.css" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="site-app.css"></noscript>
"""

FONT_BLOCK_OLD = re.compile(
    r'<link rel="preload" as="style" href="https://fonts\.googleapis\.com/css2\?[^"]+">\s*'
    r'<link href="https://fonts\.googleapis\.com/css2\?[^"]+" rel="stylesheet">\s*',
    re.DOTALL,
)

FONT_BLOCK_NEW = """<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap"></noscript>
"""


def main() -> None:
    index_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INDEX
    css_path = DEFAULT_CSS
    text = index_path.read_text(encoding="utf-8")

    if "site-app.css" in text and 'id="site-critical"' in text:
        print("extract_site_app_css.py: 既に切り出し済みです")
        return

    m = STYLE_BLOCK_RE.search(text)
    if not m:
        raise SystemExit("extract_site_app_css.py: <style> ブロックが見つかりません")

    css_body = m.group(1).strip() + "\n"
    css_path.write_text(css_body, encoding="utf-8")
    print(f"extract_site_app_css.py: {css_path} ({len(css_body)} bytes)")

    text = STYLE_BLOCK_RE.sub(CRITICAL_CSS + "\n", text, count=1)
    text = FONT_BLOCK_OLD.sub(FONT_BLOCK_NEW, text, count=1)
    index_path.write_text(text, encoding="utf-8")
    print(f"extract_site_app_css.py: {index_path} を更新しました")


if __name__ == "__main__":
    main()
