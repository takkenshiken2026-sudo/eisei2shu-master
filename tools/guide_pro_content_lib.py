"""試験ガイド記事のプロ品質文案生成。"""
from __future__ import annotations

import re
from typing import Any

# スラッグ別の手作り上書き（apply 時にマージ）
try:
    from pro_content.guide_enrichments import GUIDE_ENRICHMENTS  # type: ignore
except ImportError:
    GUIDE_ENRICHMENTS: dict[str, dict[str, str]] = {}


def topic_from_title(title: str) -> str:
    t = re.sub(r"【[^】]+】", "", title)
    t = re.sub(r"｜.+$", "", t)
    return t.strip() or title


def polish_lead(article: dict[str, str]) -> str:
    slug = article.get("slug", "")
    title = topic_from_title(article.get("title", ""))
    genre = article.get("genre", "試験対策")
    existing = (article.get("lead") or "").strip()
    if len(existing) > 120 and "結論" in existing[:80]:
        base = existing
    else:
        base = f"「{title}」について、第二種衛生管理者試験の受験者が迷いやすい点を整理します。"
    return (
        f"{base} "
        f"本記事は{genre}の観点から、試験頻出の数値・手続き・誤りやすい表現を専門的に解説します。"
        f"独学・現場経験のどちらの方も、過去問で得点につなげられるよう設計しています。"
    )


def section_bodies_fallback(article: dict[str, str]) -> dict[str, str]:
    title = topic_from_title(article.get("title", ""))
    genre = article.get("genre", "試験対策")
    tags = article.get("tags", "")

    s1 = (
        f"## この記事の結論\n"
        f"{title}は、第二種衛生管理者試験において{genre}の文脈で繰り返し問われるテーマです。"
        f"法令・告示の数値、実施主体（事業者・衛生管理者・産業医）、記録保存期間のいずれかが"
        f"選択肢の言い換えとして出題されます。まず「義務か努力か」「誰が行うか」「いつまで保存か」"
        f"の3軸で整理してから、細部の数値を覚える順番が効率的です。"
    )
    s2 = (
        f"## 試験での出題パターン\n"
        f"過去問では、{title}に関して次のような問い方が多く見られます。"
        f"①定義・目的の確認 ②数値条件（％、ppm、年、月、人数）の正誤 ③他制度との混同"
        f"（定期健診と特殊健診、局所排気と全体換気など） ④記録・保存期間の抜け。"
        f"選択肢はどれか一つが明確に誤り、残りが「一見正しそう」な表現になっていることが特徴です。"
    )
    s3 = (
        f"## 押さえるべきポイント（チェックリスト）\n"
        f"・{title}の法的根拠（労働安全衛生法・規則・関係告示）を一言で言える\n"
        f"・実施義務の主体（事業者／衛生管理者／産業医）を区別できる\n"
        f"・頻出数値を単位つきで暗記している（18％、6か月、1年、30年など）\n"
        f"・関連する用語解説・過去問とセットで復習している\n"
        f"・最新の試験要項・公式資料で改定がないか確認した"
    )
    s4 = (
        f"## よくある誤解と対策\n"
        f"「努力規定だから実施しなくてよい」「記録は任意」「パートタイムは対象外」"
        f"といった誤りは、{title}を含む多くのテーマで共通のひっかけです。"
        f"対策として、条文の主語をメモし、数値は「条件＋単位」でカード化してください。"
        f"また、類似制度（教育・健診・測定）と表で比較すると、試験本番での判断速度が上がります。"
    )
    s5 = (
        f"## 学習・復習の進め方\n"
        f"初回は本記事と関連する用語解説を読み、全体像をつかみます。"
        f"次に、{genre}の過去問で{title}に触れる問題を3〜5問解き、誤り肢のパターンを記録します。"
        f"最後に、数値と主体だけを声に出して説明できるかセルフチェックします。"
        f"タグ（{tags or '試験対策'}）が付いた関連記事もあわせて読むと、知識が網目状につながります。"
    )
    s6 = (
        f"## 受験直前の最終確認\n"
        f"試験前週は新しいテキストを増やさず、本記事のチェックリストと過去問の誤答ノートを見直すだけで十分です。"
        f"当日は、問題文の主語（誰が）と数値の単位に線を引く習慣をつけてください。"
    )

    return {
        "section_1_heading": "結論と試験での位置づけ",
        "section_1_body": s1,
        "section_2_heading": "出題パターンと頻出の問われ方",
        "section_2_body": s2,
        "section_3_heading": "押さえるべきチェックリスト",
        "section_3_body": s3,
        "section_4_heading": "よくある誤解と対策",
        "section_4_body": s4,
        "section_5_heading": "学習・復習の進め方",
        "section_5_body": s5,
        "section_6_heading": "受験直前の最終確認",
        "section_6_body": s6,
        "section_7_heading": "",
        "section_7_body": "",
    }


def expert_faqs_guide(article: dict[str, str]) -> dict[str, str]:
    title = topic_from_title(article.get("title", ""))
    genre = article.get("genre", "")
    return {
        "faq_1_question": f"「{title}」は第二種衛生管理者試験でどの程度重要ですか？",
        "faq_1_answer": (
            f"{genre}のテーマとして頻出です。科目全体の得点源になるため、"
            f"定義だけでなく数値・主体・記録までセットで押さえることをおすすめします。"
        ),
        "faq_2_question": f"独学で「{title}」を勉強する順番は？",
        "faq_2_answer": (
            "①本記事で全体像 ②関連用語解説 ③過去問3〜5問 ④誤り肢ノート作成。"
            "テキストの該当章は、過去問で間違えたあとに読み返すと効率がよいです。"
        ),
        "faq_3_question": f"「{title}」でよくあるひっかけは？",
        "faq_3_answer": (
            "努力規定と義務の取り違え、実施主体の混同、保存期間の数値違いが代表例です。"
            "選択肢は「一見正しそう」な表現が並ぶため、主語と数値に線を引く習慣が有効です。"
        ),
        "faq_4_question": "公式情報はどこで確認すべきですか？",
        "faq_4_answer": (
            "安全衛生技術試験協会の試験要項、厚生労働省の職場のあんぜんサイト、"
            "e-Gov法令検索で最新の条文・告示を確認してください。本記事は学習整理用です。"
        ),
    }


def enrich_article(article: dict[str, str], *, force_sections: bool) -> dict[str, str]:
    slug = article.get("slug", "")
    out: dict[str, str] = {}
    out["lead"] = polish_lead(article)
    out.update(expert_faqs_guide(article))

    total = sum(len(article.get(f"section_{i}_body", "")) for i in range(1, 8))
    custom = GUIDE_ENRICHMENTS.get(slug, {})
    if custom:
        out.update(custom)
    elif force_sections or total < 900:
        out.update(section_bodies_fallback(article))

    meta = article.get("meta_description", "")
    if len(meta) < 80:
        title = topic_from_title(article.get("title", ""))
        out["meta_description"] = (
            f"{title}を第二種衛生管理者試験向けに専門解説。"
            f"頻出の数値・誤り肢・学習手順を整理。独学・直前対策に対応。"
        )
    return out


def patch_row(row: dict[str, str]) -> None:
    total = sum(len(row.get(f"section_{i}_body", "")) for i in range(1, 8))
    updates = enrich_article(row, force_sections=total < 900)
    for key, val in updates.items():
        if val or key.startswith("section_"):
            row[key] = val
