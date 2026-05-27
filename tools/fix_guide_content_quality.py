#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ガイド記事: 汎用追記の除去・重複段落の整理・表形式の修復。"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.glossary_link_lib import article_term_lookup, term_name_to_markdown_link

GUIDE_CSV = ROOT / "data" / "guide_articles.csv"
GENERIC_ADDON = (
    "第二種衛生管理者試験では、この見出しの内容が他のテーマと組み合わされて出題されることがあります。"
    "関連リンクの用語・ガイドもあわせて確認し、知識を孤立させないようにしてください。"
)
GENERIC_ADDON_CORE = (
    "この見出しの内容が他のテーマと組み合わされて出題されることがあります。"
    "関連リンクの用語・ガイドもあわせて確認し、知識を孤立させないようにしてください。"
)

CATEGORY_TERM_LISTS: dict[str, list[str]] = {
    "category-kankeihorei": [
        "衛生管理者",
        "労働安全衛生法",
        "産業医",
        "総括安全衛生管理者",
        "衛生委員会",
        "定期健康診断",
        "作業環境測定",
        "有機溶剤中毒予防規則",
        "特定化学物質障害予防規則",
        "石綿障害予防規則",
        "じん肺法",
        "酸素欠乏症等防止規則",
    ],
    "category-rodoeisei": [
        "WBGT",
        "局所排気装置",
        "リスクアセスメント",
        "作業環境評価",
        "捕集分析法",
        "A測定・B測定",
        "作業環境管理区分",
        "許容濃度",
        "保護具",
        "SDS",
        "全面換気",
        "騒音の測定",
    ],
    "category-rodoseiri": [
        "熱中症",
        "一酸化炭素",
        "じん肺",
        "騒音性難聴",
        "振動障害",
        "有機溶剤",
        "ベンゼン",
        "粉じん",
        "確定的影響と確率的影響",
        "代謝率",
        "酸素欠乏症",
    ],
}

CATEGORY_SECTION_2: dict[str, tuple[str, str]] = {
    "category-kankeihorei": (
        "関係法令の試験対策",
        "試験では数値・条件の正確な暗記が求められます。単語だけでなく「なぜその数値か」を理解することが合格への近道です。\n\n"
        "→ [頻出数値 完全暗記リスト](../suuchi-anki-list/)\n\n"
        "→ [過去問を解いてみる（無料）](../../index.html#past)",
    ),
    "category-rodoeisei": (
        "労働衛生の試験対策",
        "計算式（WBGT・換気量など）と装置の構成順序は、過去問で繰り返し問われます。用語の定義だけでなく、数値の単位と「いつ使う式か」をセットで覚えてください。\n\n"
        "→ [WBGTの計算式まとめ](../wbgt-keisan/)\n\n"
        "→ [過去問を解いてみる（無料）](../../index.html#past)",
    ),
    "category-rodoseiri": (
        "労働生理の試験対策",
        "人体の反応（代謝・循環・神経）と環境要因の関係が問われます。図や数値より「条件が変わると何が起きるか」の因果で整理すると得点しやすくなります。\n\n"
        "→ [労働生理のまとめ](../rodo-seiri-matome/)\n\n"
        "→ [過去問を解いてみる（無料）](../../index.html#past)",
    ),
}

MANUAL_SECTION_BODIES: dict[str, dict[int, str]] = {
    "3kagetsu-goukaku": {
        1: (
            "[table]\n"
            "期間|重点|目標\n"
            "1〜4週目|テキスト通読・数値整理|3科目を一通り読み、重要数値に印をつける\n"
            "5〜8週目|科目別演習|分野ごとに理解度チェック、弱点を特定\n"
            "9〜11週目|過去問|直近3〜5回分を解説まで読み込む\n"
            "12週目|直前調整|数値・誤りやすい条件の最終確認\n"
            "[/table]"
        ),
        2: (
            "[table]\n"
            "科目|割合|ポイント\n"
            "関係法令|40%|選任人数・健診頻度・保存期間を表にまとめる\n"
            "労働衛生|35%|局所排気・測定・管理区分を図で整理\n"
            "労働生理|25%|毎日少しずつ。後回しにしない\n"
            "[/table]\n\n"
            "→ [6ヶ月プランはこちら](../6kagetsu-keikaku/)\n\n"
            "→ [頻出数値 完全暗記リスト](../suuchi-anki-list/)"
        ),
    },
    "bookmark-fukushu": {
        1: (
            "[table]\n"
            "タイミング|やること\n"
            "当日|誤り理由を1行メモ。正解の根拠を声に出す\n"
            "翌日|印のついた問題だけ再解答（テキストは見ない）\n"
            "1週間後|まだ間違う問題は関連用語記事を読む\n"
            "[/table]"
        ),
    },
}


def atomic_write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def strip_generic_addon(body: str) -> tuple[str, int]:
    count = 0
    for fragment in (GENERIC_ADDON, GENERIC_ADDON_CORE):
        while fragment in body:
            body = body.replace(fragment, "")
            count += 1
    body = re.sub(r"第二種(?:\[[^\]]+\]\([^)]+\))?衛生管理者試験では、+", "第二種衛生管理者試験では、", body)
    return body.strip(), count


def dedupe_paragraphs(body: str) -> str:
    parts = [p.strip() for p in re.split(r"\n{2,}", body.strip()) if p.strip()]
    if not parts:
        return body.strip()
    seen: set[str] = set()
    unique: list[str] = []
    for part in parts:
        if part in seen:
            continue
        seen.add(part)
        unique.append(part)
    return "\n\n".join(unique)


def category_terms_body(slug: str, lookup: dict[str, str]) -> str:
    names = CATEGORY_TERM_LISTS.get(slug, [])
    if not names:
        return ""
    linked = ";".join(term_name_to_markdown_link(t, lookup) for t in names)
    return linked + "\n\n→ [全用語解説一覧（267本）はこちら](../../terms/index.html)"


def main() -> int:
    text = GUIDE_CSV.read_text(encoding="utf-8-sig")
    rows = list(csv.DictReader(text.splitlines()))
    fieldnames = list(rows[0].keys()) if rows else []
    lookup = article_term_lookup()
    stripped_addon = 0
    category_fixed = 0
    deduped = 0
    manual_fixed = 0

    for row in rows:
        slug = (row.get("slug") or "").strip()
        manual = MANUAL_SECTION_BODIES.get(slug, {})

        for idx in range(1, 9):
            key = f"section_{idx}_body"
            if idx in manual:
                row[key] = manual[idx]
                manual_fixed += 1
                continue
            body = row.get(key) or ""
            if not body:
                continue
            new_body, n = strip_generic_addon(body)
            cleaned = dedupe_paragraphs(new_body)
            if cleaned != body:
                if cleaned != new_body:
                    deduped += 1
                row[key] = cleaned
            elif n:
                row[key] = new_body
                stripped_addon += n

        if slug in CATEGORY_TERM_LISTS:
            row["section_1_body"] = category_terms_body(slug, lookup)

        if slug in CATEGORY_SECTION_2:
            heading, body = CATEGORY_SECTION_2[slug]
            row["section_2_heading"] = heading
            row["section_2_body"] = body
            category_fixed += 1

    atomic_write_csv(GUIDE_CSV, fieldnames, rows)
    print(f"Removed generic addon from {stripped_addon} section(s)")
    print(f"Deduped paragraphs in {deduped} section(s)")
    print(f"Manual section fixes: {manual_fixed}")
    print(f"Restored category section 2 for {category_fixed} article(s)")
    print(f"Updated {GUIDE_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
