#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ガイド記事: 汎用追記の除去・重複段落の整理・表形式の修復。"""
from __future__ import annotations

import csv
import io
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
        2: (
            "転記に時間をかけすぎないよう、問題番号＋誤った理由（数値ミス／条文混同など）をコード化すると復習が速くなります。\n\n"
            "→ [本サイトの過去問演習](../../index.html#past)と併用すると、間違えた問題を科目別に振り返れます。"
        ),
    },
    "6kagetsu-keikaku": {
        1: (
            "[table]\n"
            "月|やること\n"
            "1〜2ヶ月目|関係法令を中心にテキスト通読。数値は自分の一覧表を作成\n"
            "3〜4ヶ月目|労働衛生・労働生理を追加。用語解説で理解を補強\n"
            "5ヶ月目|過去問を解き、解説を熟読\n"
            "6ヶ月目|弱点科目の反復・直前は新規インプットを控える\n"
            "[/table]"
        ),
        2: (
            "週末15分：その週に学んだ数値だけ声に出して確認\n"
            "月1回：間違えた問題だけ再挑戦\n\n"
            "→ [間違え問題の復習サイクル](../bookmark-fukushu/)\n\n"
            "試験2ヶ月前：申込・会場確認まで完了させる\n\n"
            "→ [3ヶ月プラン](../3kagetsu-goukaku/) ／ [独学合格ガイド](../dokugaku-guide/) ／ [通信講座と独学の比較](../tsushin-kouza-vs-dokugaku/)"
        ),
    },
    "ichimon-ittou": {
        1: (
            "[table]\n"
            "ステップ|内容\n"
            "1|テキストで該当分野を読んでから問題に取り組む\n"
            "2|不正解は理由を1行でメモ（なぜ他の肢が誤りか）\n"
            "3|24時間後・1週間後に同じ問題だけ再挑戦\n"
            "[/table]"
        ),
        2: (
            "向いている：数値、保存期間、選任人数、用語定義\n"
            "向いていない：複数条件の組み合わせ問題（過去問形式で練習）\n\n"
            "→ [過去問は何年分](../kakomon-nannennbun/) ／ [おすすめ学習アプリ](../osusume-app/) ／ [出題傾向の把握](../shutsudai-keiko/)"
        ),
    },
    "jikan-haibun": {
        1: (
            "[table]\n"
            "フェーズ|時間|内容\n"
            "第1周|120分|得意科目から解く。1問4〜5分を目安\n"
            "第2周|45分|見直し・迷った問題・計算問題\n"
            "予備|15分|マークミス確認・解答欄の記入漏れ\n"
            "[/table]"
        ),
        2: (
            "関係法令：数値・条件の問題は早めに処理\n"
            "労働衛生：図表問題は読み込みに時間がかかるため中盤に配置\n"
            "労働生理：知識問題は直感で、不明は印をつけて後回し\n\n"
            "→ [試験当日の流れ](../shiken-tojitsu-nagare/) ／ [合格基準・足切り](../goukaku-kijun/) ／ [試験科目と出題範囲](../shiken-kamoku/)"
        ),
    },
    "kanri-kubun-oboekata": {
        2: (
            "「第1管理＝最も良い環境」→ 誤り（改善が必要な側）\n"
            "「措置は1回で終わり」→ 再測定・再評価が必要な場面がある\n\n"
            "→ [措置A](../../terms/sochi-a.html) ／ [措置B](../../terms/sochi-b.html) ／ [作業環境管理の流れ](../sagyo-kankyo-kanri-flow/)"
        ),
    },
    "niji-kenko-shindan-guide": {
        1: (
            "[table]\n"
            "段階|内容\n"
            "一次健康診断|定期・雇入時など\n"
            "所見・通知|医師の意見、労働者への通知\n"
            "二次健康診断|精密検査の実施\n"
            "就業上の措置|就業禁止・配置転換など\n"
            "[/table]\n\n"
            "→ [就業上の措置](../../terms/shugyo-jo-sochi.html)\n\n"
            "実施時期・通知期限などの数値は、受験前に公式情報・テキストで最新を確認してください。\n\n"
            "→ [健康診断後の事後措置](../kenko-shindan-jigo-tejun/) ／ [健康診断の頻度](../kenko-shindan-hindo/)"
        ),
    },
    "sagyo-shunin-ichiran": {
        2: (
            "作業主任者は特定作業の現場指揮、衛生管理者は事業場全体の衛生管理です。"
            "どちらか一方がいれば足りる、という整理は誤りになりやすい点に注意してください。\n\n"
            "→ [作業主任者](../../terms/sagyoshunin-sha.html) ／ [特別教育の実施時期](../tokubetsu-kyoiku-jugyomae/) ／ [有機溶剤の区分と義務](../yuki-yozai-kubun-gimu/)"
        ),
    },
    "saijuken-taisaku": {
        1: (
            "[table]\n"
            "確認項目|対策\n"
            "足切り科目があるか|最も得点が低い科目を優先的に補強\n"
            "数値問題の正答率|数値暗記リストで再整理\n"
            "過去問の解説を読んだか|正解問題も含め解説を音読する\n"
            "勉強時間が足りたか|3ヶ月以上の計画に切り替える\n"
            "[/table]"
        ),
        2: (
            "1〜3週目：足切り科目のテキストを再読＋演習\n"
            "4〜6週目：過去問を本番形式で2回分\n"
            "7〜8週目：間違え問題のみ反復、数値の最終確認\n\n"
            "→ [合格ラインと落ちる理由](../goukaku-kijun/) ／ [合格率・難易度](../goukakuritsu/) ／ [何問正解で合格か](../goukaku-kijun/)"
        ),
    },
    "shiken-tojitsu-nagare": {
        1: (
            "[table]\n"
            "段階|内容\n"
            "到着|開始30〜60分前を目安に会場へ。交通遅延を想定\n"
            "受付|受験票・身分証明書を提示\n"
            "着席|指定席・解答用紙の記入事項を確認\n"
            "試験開始|合図後に解答。途中退出の可否は案内に従う\n"
            "終了|提出・退場。結果は後日発表\n"
            "[/table]\n\n"
            "注意：携帯電話・スマートウォッチ等の持ち込み制限は会場案内に従ってください。\n\n"
            "→ [当日の持ち物](../shiken-tojitsu-mochimono/) ／ [試験会場・アクセス](../shiken-kaijo/) ／ [時間配分の目安](../jikan-haibun/)"
        ),
    },
}

USER_INTENT_TEMPLATE = "について試験前に整理したい"
GARBAGE_RELATED_RE = re.compile(r"\s{2,}関連するガイド・用語(?:\s{2,}[^\n]+)?")
INLINE_LINK_FIXES: list[tuple[str, str]] = [
    ("(→ 間違え問題の復習サイクル)", "→ [間違え問題の復習サイクル](../bookmark-fukushu/)"),
    ("→ 試験当日の流れ", "→ [試験当日の流れ](../shiken-tojitsu-nagare/)"),
    ("→ 措置A ／ 措置B", "→ [措置A](../../terms/sochi-a.html) ／ [措置B](../../terms/sochi-b.html)"),
]


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


def fix_user_intent(row: dict[str, str]) -> bool:
    ui = (row.get("user_intent") or "").strip()
    if USER_INTENT_TEMPLATE not in ui:
        return False
    lead = (row.get("lead") or "").strip()
    meta = (row.get("meta_description") or "").strip()
    row["user_intent"] = (lead or meta or ui.replace(USER_INTENT_TEMPLATE, "の要点を整理する"))[:240]
    return True


def clean_section_body(body: str) -> str:
    body = GARBAGE_RELATED_RE.sub("", body).strip()
    for old, new in INLINE_LINK_FIXES:
        body = body.replace(old, new)
    return body.strip()


def main() -> int:
    with GUIDE_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []
    lookup = article_term_lookup()
    stripped_addon = 0
    category_fixed = 0
    deduped = 0
    manual_fixed = 0
    user_intent_fixed = 0
    garbage_stripped = 0

    for row in rows:
        slug = (row.get("slug") or "").strip()
        if fix_user_intent(row):
            user_intent_fixed += 1
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
            cleaned_garbage = clean_section_body(body)
            if cleaned_garbage != body:
                garbage_stripped += 1
                body = cleaned_garbage
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
    print(f"Fixed user_intent: {user_intent_fixed} article(s)")
    print(f"Stripped migration garbage from {garbage_stripped} section(s)")
    print(f"Removed generic addon from {stripped_addon} section(s)")
    print(f"Deduped paragraphs in {deduped} section(s)")
    print(f"Manual section fixes: {manual_fixed}")
    print(f"Restored category section 2 for {category_fixed} article(s)")
    print(f"Updated {GUIDE_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
