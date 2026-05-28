#!/usr/bin/env python3
"""
index.html の PageSpeed 向けパッチ（レンダリングブロック軽減）。
- 構造化データを </body> 直前へ移動
- site-theme.css を head 先頭付近へ
- データ JS / アプリ JS に defer
- Supabase SDK を遅延読み込み

使い方:
  python3 tools/patch_index_performance.py
  python3 tools/patch_index_performance.py path/to/index.html
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = ROOT / "index.html"

LD_JSON_RE = re.compile(
    r'<script type="application/ld\+json">.*?</script>\s*',
    re.DOTALL,
)

SUPABASE_HEAD = re.compile(
    r'\n<script src="https://cdn\.jsdelivr\.net/npm/@supabase/supabase-js@2"></script>',
)

SUPABASE_INIT = re.compile(
    r"const _sb = window\.supabase\.createClient\(SUPABASE_URL, SUPABASE_KEY\);",
)

THEME_AT_HEAD_END = re.compile(
    r'\n\s*<link rel="stylesheet" href="site-theme\.css">\s*\n</head>',
)

DATA_SCRIPTS = re.compile(
    r'(<script)( src="eisei2-data-(?:glossary|original)\.js")></script>\s*'
    r'(<script)( src="eisei2-master-data\.js")></script>',
)

MAIN_APP_SCRIPT = re.compile(
    r"(<script src=\"eisei2-master-data\.js\"></script>\s*)\n<script>\s*\n\n\(function enrichGlossaryPlaceholderDesc",
)

SUPABASE_HELPERS = """let _sb = null;
let _sbSdkPromise = null;

function loadSupabaseSdk() {
  if (window.supabase) return Promise.resolve();
  if (_sbSdkPromise) return _sbSdkPromise;
  _sbSdkPromise = new Promise(function (resolve, reject) {
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';
    s.defer = true;
    s.crossOrigin = 'anonymous';
    s.onload = function () { resolve(); };
    s.onerror = function () { reject(new Error('Supabase SDK load failed')); };
    document.head.appendChild(s);
  });
  return _sbSdkPromise;
}

async function getSupabaseClient() {
  await loadSupabaseSdk();
  if (!_sb) _sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
  return _sb;
}"""


def patch(text: str) -> str:
    blocks = LD_JSON_RE.findall(text)
    if len(blocks) < 2:
        raise SystemExit(
            f"patch_index_performance.py: 構造化データ script が {len(blocks)} 件（2件想定）"
        )
    text = LD_JSON_RE.sub("", text, count=len(blocks))

    if "loadSupabaseSdk" not in text:
        text = SUPABASE_HEAD.sub("", text, count=1)
        text = SUPABASE_INIT.sub(SUPABASE_HELPERS, text, count=1)
        text = text.replace(
            "await _sb.from(USER_LEARNING_SYNC_TABLE)",
            "await (await getSupabaseClient()).from(USER_LEARNING_SYNC_TABLE)",
        )
        text = text.replace(
            "await _sb\n    .from('user_answers')",
            "await (await getSupabaseClient())\n    .from('user_answers')",
        )
        text = text.replace(
            "await _sb.from('user_answers')",
            "await (await getSupabaseClient()).from('user_answers')",
        )
        text = text.replace(
            "({data,error}=await _sb.auth.",
            "({data,error}=await (await getSupabaseClient()).auth.",
        )
        text = text.replace("await _sb.auth.", "await (await getSupabaseClient()).auth.")
        text = text.replace(
            "const {data:{session}}=await _sb.auth.getSession();",
            "const {data:{session}}=await (await getSupabaseClient()).auth.getSession();",
        )

    if 'rel="preload" href="site-theme.css"' not in text:
        text = text.replace(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">\n'
            '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>\n'
            '<link rel="dns-prefetch" href="https://ujysjdaboqqslkljjjtn.supabase.co">\n'
            '<link rel="preload" href="site-theme.css" as="style">\n'
            '<link rel="stylesheet" href="site-theme.css">',
            1,
        )

    text = THEME_AT_HEAD_END.sub("\n</head>", text, count=1)

    text = DATA_SCRIPTS.sub(r'\1 defer\2></script>\n\3 defer\4></script>', text, count=1)

    if 'eisei2-master-data.js"></script>\n<script defer>' not in text:
        text = text.replace(
            '<script src="eisei2-master-data.js"></script>\n<script>\n\n(function enrichGlossaryPlaceholderDesc',
            '<script defer src="eisei2-master-data.js"></script>\n<script defer>\n\n(function enrichGlossaryPlaceholderDesc',
            1,
        )

    footer_ld = "\n".join(blocks) + "\n"
    if footer_ld.strip() not in text:
        text = re.sub(r"</body>\s*</html>\s*$", footer_ld + "</body>\n</html>\n", text, count=1)

    return text


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TARGET
    if not target.is_file():
        print(f"patch_index_performance.py: ファイルがありません: {target}", file=sys.stderr)
        sys.exit(1)
    original = target.read_text(encoding="utf-8")
    updated = patch(original)
    if updated == original:
        print(f"patch_index_performance.py: 変更なし ({target})")
        return
    target.write_text(updated, encoding="utf-8")
    print(f"patch_index_performance.py: OK ({target})")


if __name__ == "__main__":
    main()
