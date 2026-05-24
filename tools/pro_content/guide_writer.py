"""試験ガイド（guide_articles.csv）向け・専門家品質への引き上げ。"""
from __future__ import annotations

import re

EXAM_NAME = "第二種衛生管理者試験"

GENRE_LEAD_TAIL = {
    "試験対策": "受験戦略と出題傾向の両面から、迷いやすい判断を整理しました。",
    "分野別対策": "科目ごとの得点源と時間配分を意識した内容です。",
    "試験概要": "試験制度の全体像を、初めて調べる方にも伝わる順序で説明しています。",
    "学習計画": "働きながらでも続けられるよう、週単位のイメージを持てる構成にしています。",
    "独学対策": "独学で陥りがちな勘違いと、効率のよい進め方を明示しています。",
    "直前・当日": "直前期にやること・やらないことを切り分け、当日の不安を減らします。",
    "合格・難易度": "数字の読み方と、自分の位置づけの考え方を整理します。",
    "受験・申込": "手続きの抜け漏れを防ぐチェックリストとして使えます。",
    "過去問活用": "解き方の型と、復習の回し方に焦点を当てています。",
    "用語整理": "用語のつながりを押さえ、科目横断の理解を助けます。",
}


def split_semicolon(value: str) -> list[str]:
    return [x.strip() for x in re.split(r"[;；]", value or "") if x.strip()]


def professional_lead(title: str, genre: str, existing: str) -> str:
    existing = (existing or "").strip()
    tail = GENRE_LEAD_TAIL.get(genre, "受験生の疑問に答える形で構成しています。")
    if len(existing) > 80 and "。" in existing:
        return f"{existing} 本記事は{EXAM_NAME}に特化し、{tail}"
    return (
        f"「{title}」について、{EXAM_NAME}を目指す方の視点で解説します。"
        f"{tail} 公式の試験要項とあわせてご確認ください。"
    )


def boost_section_body(heading: str, body: str, genre: str, title: str) -> str:
    body = (body or "").strip()
    if len(body) >= 320 or body.count("\n") >= 8:
        return body
    heading = heading.strip()
    addon = ""
    if "計画" in heading or "ロードマップ" in heading or "スケジュール" in title:
        addon = (
            "\n\n週ごとに「インプット週」と「過去問週」を交互に置くと、知識の定着と解法の型が両立しやすくなります。"
            "完璧主義にならず、未消化分は次週に持ち越す前提で設計してください。"
        )
    elif "違い" in heading or "比較" in heading:
        addon = (
            "\n\n表の数字は年度で変わることがあるため、受験直前には安全衛生技術試験協会の最新資料で確認してください。"
            "試験では「どちらが厳しいか」より「自分の職場にどちらが必要か」が問われることがあります。"
        )
    elif "過去問" in heading:
        addon = (
            "\n\n1問あたりの目安時間を意識し、解説を読むときは「なぜ他の肢が誤りか」まで言語化すると実力が残ります。"
        )
    elif genre == "分野別対策":
        addon = (
            "\n\n苦手科目は“丸暗記”より、過去問で出た論点リストを作り、用語ページと往復する復習が効率的です。"
        )
    else:
        addon = (
            f"\n\n{EXAM_NAME}では、この見出しの内容が他のテーマと組み合わされて出題されることがあります。"
            "関連リンクの用語・ガイドもあわせて確認し、知識を孤立させないようにしてください。"
        )
    return body + addon


def professional_faqs(title: str, genre: str, lead: str) -> list[tuple[str, str]]:
    return [
        (
            f"「{title}」は、どんな人が読むと効果的ですか？",
            f"初めて{EXAM_NAME}を調べる方、受験時期を決めた方、{genre}で迷っている方に向けた記事です。"
            f"{lead[:100]}…" if len(lead) > 100 else lead,
        ),
        (
            "独学でもこの内容は活かせますか？",
            "はい。本記事は独学向けに、やること・やらないことを切り分けています。"
            "過去問と用語解説を組み合わせると、理解が定着しやすくなります。",
        ),
        (
            "試験要項と食い違う場合はどちらを優先しますか？",
            "必ず安全衛生技術試験協会の最新試験要項・公式発表を優先してください。"
            "本記事は学習の整理用であり、制度変更は随時反映が必要です。",
        ),
        (
            "読んだあと、次に何をすればよいですか？",
            "関連リンクの用語ページでキーワードを確認し、"
            f"{EXAM_NAME}の過去問で同テーマの問題を3問程度解いてみてください。"
            "解けなかった論点だけをノートに残すと復習効率が上がります。",
        ),
    ]


def enrich_guide_row(row: dict) -> dict:
    title = (row.get("title") or "").strip()
    genre = (row.get("genre") or "試験対策").strip()
    lead = professional_lead(title, genre, row.get("lead", ""))
    row["lead"] = lead

    for idx in range(1, 8):
        h = (row.get(f"section_{idx}_heading") or "").strip()
        b = row.get(f"section_{idx}_body") or ""
        if h and b.strip():
            row[f"section_{idx}_body"] = boost_section_body(h, b, genre, title)

    faqs = professional_faqs(title, genre, lead)
    for i, (q, a) in enumerate(faqs, 1):
        row[f"faq_{i}_question"] = q
        row[f"faq_{i}_answer"] = a

    meta = (row.get("meta_description") or "").strip()
    if len(meta) < 40:
        row["meta_description"] = (
            f"{title}について、{EXAM_NAME}受験生向けに要点を整理。"
            f"{GENRE_LEAD_TAIL.get(genre, '')}"
        )[:155]
    return row
