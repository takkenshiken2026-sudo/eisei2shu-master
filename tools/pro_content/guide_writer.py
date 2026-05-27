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


EXAM_SPECIALIZE_PREFIX = f"本記事は{EXAM_NAME}に特化し、"

LEAD_BOILERPLATE_MARKERS = (
    f"について、{EXAM_NAME}を目指す方の視点で解説",
    f"について、{EXAM_NAME}の受験者が迷いやすい点を整理",
)


def topic_from_title(title: str) -> str:
    t = re.sub(r"【[^】]+】", "", title)
    t = re.sub(r"｜.+$", "", t)
    return t.strip() or title


def is_boilerplate_lead(text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return True
    return any(marker in text for marker in LEAD_BOILERPLATE_MARKERS)


def is_generic_faq(row: dict[str, str]) -> bool:
    answer = (row.get("faq_1_answer") or "").strip()
    question = (row.get("faq_1_question") or "").strip()
    faq3 = (row.get("faq_3_answer") or "").strip()
    if is_boilerplate_lead(answer) or "公…" in answer:
        return True
    if "どんな人が読むと効果的" in question and "初めて第二種衛生管理者試験を調べる方" in answer:
        if "受験時期を決めた方" not in answer:
            return True
    if "努力規定と義務の取り違え" in faq3:
        return True
    if "科目全体の得点源になるため" in answer:
        return True
    return False


def lead_from_row(row: dict[str, str]) -> str:
    """公開用リード: 定型文を除き meta または既存の有用な文を採用。"""
    meta = (row.get("meta_description") or "").strip()
    existing = dedupe_guide_lead((row.get("lead") or "").strip())
    if EXAM_SPECIALIZE_PREFIX in existing:
        first = existing.find(EXAM_SPECIALIZE_PREFIX)
        before = existing[:first].strip()
        if before and not is_boilerplate_lead(before):
            existing = before
    if existing and not is_boilerplate_lead(existing) and len(existing) >= 24:
        return existing
    if meta and not is_boilerplate_lead(meta):
        return meta
    title = topic_from_title((row.get("title") or "").strip())
    return f"{title}について、{EXAM_NAME}受験生が押さえる要点を整理します。"


def dedupe_guide_lead(lead: str) -> str:
    """複数回 enrich された際に重複するリード文の定型句を1回に戻す。"""
    lead = (lead or "").strip()
    if EXAM_SPECIALIZE_PREFIX not in lead:
        return lead
    first = lead.find(EXAM_SPECIALIZE_PREFIX)
    before = lead[:first].strip()
    rest = lead[first + len(EXAM_SPECIALIZE_PREFIX) :]
    second = rest.find(EXAM_SPECIALIZE_PREFIX)
    tail = rest[:second].strip() if second >= 0 else rest.strip()
    return f"{before} {EXAM_SPECIALIZE_PREFIX}{tail}".strip()


def professional_lead(title: str, genre: str, existing: str, meta: str = "") -> str:
    """リードを引き上げる。定型の「目指す方の視点で解説」は生成しない。"""
    row = {"title": title, "genre": genre, "lead": existing, "meta_description": meta}
    return lead_from_row(row)


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
    return body + addon if addon else body


def professional_faqs(title: str, genre: str, lead: str) -> list[tuple[str, str]]:
    lead_summary = dedupe_guide_lead(lead)
    if len(lead_summary) > 120:
        lead_summary = lead_summary[:120].rstrip("、。") + "…"
    return [
        (
            f"「{title}」は、どんな人が読むと効果的ですか？",
            f"初めて{EXAM_NAME}を調べる方、受験時期を決めた方、{genre}で迷っている方に向けた記事です。"
            f"{lead_summary}",
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
    tags = split_semicolon(row.get("tags") or "")
    if "アフィリエイト" in tags:
        meta = (row.get("meta_description") or "").strip()
        if len(meta) < 40:
            title = (row.get("title") or "").strip()
            genre = (row.get("genre") or "試験対策").strip()
            row["meta_description"] = (
                f"{title}について、{EXAM_NAME}受験生向けに要点を整理。"
                f"{GENRE_LEAD_TAIL.get(genre, '')}"
            )[:155]
        return row

    title = (row.get("title") or "").strip()
    genre = (row.get("genre") or "試験対策").strip()
    meta = (row.get("meta_description") or "").strip()
    lead = professional_lead(title, genre, row.get("lead", ""), meta)
    row["lead"] = lead

    for idx in range(1, 8):
        h = (row.get(f"section_{idx}_heading") or "").strip()
        b = row.get(f"section_{idx}_body") or ""
        if h and b.strip():
            row[f"section_{idx}_body"] = boost_section_body(h, b, genre, title)

    if is_generic_faq(row):
        from tools.guide_pro_content_lib import expert_faqs_guide

        row.update(expert_faqs_guide(row))

    meta = (row.get("meta_description") or "").strip()
    if len(meta) < 40:
        row["meta_description"] = (
            f"{title}について、{EXAM_NAME}受験生向けに要点を整理。"
            f"{GENRE_LEAD_TAIL.get(genre, '')}"
        )[:155]
    return row
