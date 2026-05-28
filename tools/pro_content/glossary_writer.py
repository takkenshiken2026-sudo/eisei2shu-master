"""用語詳細（CSV）向け・専門家×プロライター品質の本文生成。"""
from __future__ import annotations

import re

from tools.pro_content.load_handmade import tips_from_handmade
from tools.reader_friendly_lib import CONCRETE_EXAMPLES, parse_tip_pair, strip_boilerplate

EXAM_NAME = "第二種衛生管理者試験"

CATEGORY_ANGLE = {
    "関係法令": "義務の有無・実施主体・手続き・記録保存の組み合わせ",
    "労働衛生": "測定・評価・改善措置・保護具の優先順位",
    "労働生理": "原因・症状・予防・健康影響のつながり",
}


def normalize_tip(tip: str, term: str) -> str:
    tip = tip.strip()
    if "→" in tip:
        return tip
    return f"「{term}は一部の条件だけ覚えれば足りる」→ {tip}"


def clean_tips(raw: list[str], term: str = "") -> list[str]:
    out: list[str] = []
    for t in raw:
        t = t.strip()
        if not t or t in out:
            continue
        if "類似語と混同" in t or "単独で完結" in t:
            continue
        if term:
            t = normalize_tip(t, term)
        out.append(t)
    return out[:4]


def tips_from_row(row: dict, handmade: dict | None, term: str) -> list[str]:
    tips = tips_from_handmade(handmade)
    if not tips:
        for blob in (row.get("exam_points", ""), row.get("common_mistakes", "")):
            for part in re.split(r"[;；\n]", blob or ""):
                part = part.strip()
                if part.startswith(("誤：", "×", "○")):
                    part = re.sub(r"^[誤×○：\s]+", "", part)
                if len(part) > 12:
                    tips.append(part)
    return clean_tips(tips, term)


def exam_points_text(tips: list[str]) -> str:
    lines: list[str] = []
    for tip in tips[:4]:
        _, right = parse_tip_pair(tip)
        lines.append(right or tip)
    return "；".join(lines)


def mistakes_text(tips: list[str]) -> str:
    rows: list[str] = []
    for tip in tips[:3]:
        wrong, right = parse_tip_pair(tip)
        wrong = re.sub(r"^[誤×「」\s]+", "", wrong).strip()
        if wrong and right:
            rows.append(f"× {wrong} → ○ {right}")
    return "；".join(rows) if rows else ""


def professional_summary(term: str, category: str, core: str, tips: list[str]) -> str:
    core = strip_boilerplate(core)
    angle = CATEGORY_ANGLE.get(category, "定義と条件の言い換え")
    lead = (
        f"「{term}」は、{EXAM_NAME}の{category}で何度も登場する重要語です。"
        f"{core[:120]}{'…' if len(core) > 120 else ''}"
    )
    if tips:
        _, right = parse_tip_pair(tips[0])
        if right:
            lead += f" 特に、{right[:60]}…の整理が得点の分かれ目になります。"
    return lead


def professional_example(
    term: str, slug: str, category: str, tips: list[str], related: list[str]
) -> str:
    if slug in CONCRETE_EXAMPLES:
        return CONCRETE_EXAMPLES[slug].replace("【具体例】", "").strip()
    wrong, right = parse_tip_pair(tips[0]) if tips else ("", "")
    rel = f"（関連：{related[0]}）" if related else ""
    if category == "関係法令":
        return (
            f"たとえば製造業の事業場で、監督・健診担当者が「{term}」の要件を確認する場面を想像してください。"
            f"選択肢では「{wrong or '努力規定だから任意'}」と書かれることがありますが、"
            f"実務・試験ともに{right or '義務・記録・措置の有無を条文ベースで判断する'}必要があります。{rel}"
        )
    if category == "労働衛生":
        return (
            f"たとえば作業環境測定や改善計画の説明で「{term}」が鍵になります。"
            f"数値や装置名だけを覚えるのではなく、"
            f"{right or '誰のばく露を、どの手順で評価するか'}までセットで理解してください。{rel}"
        )
    return (
        f"たとえば{category}の設問で、{term}の定義を知っていても、"
        f"症状や対策の言い換えで迷うケースがあります。"
        f"{right or '原因・経路・健康影響を一本の線でつなげる'}と解答が安定します。{rel}"
    )


def professional_definition(term: str, category: str, core: str, tips: list[str]) -> str:
    core = strip_boilerplate(core)
    if core.startswith(term) or core.startswith(f"「{term}"):
        p1 = core
    else:
        p1 = f"{term}とは、{core}"
    p2 = (
        f"現場では、事業者・衛生管理者・産業医が役割分担のなかでこの概念を使います。"
        f"{category}の問題では、単語の意味より「誰が何をしなければならないか」に落とし込めるかが重要です。"
    )
    p3 = ""
    if tips:
        wrong, right = parse_tip_pair(tips[0])
        if wrong and right:
            p3 = (
                f"試験では「{wrong}」のように聞こえる選択肢が混ざります。"
                f"正しくは、{right}と整理してから選択肢を読み進めてください。"
            )
    return "\n\n".join(x for x in (p1, p2, p3) if x)


def professional_exam_angle(term: str, category: str, tips: list[str]) -> str:
    blocks = [
        f"{EXAM_NAME}の{category}では、{term}について次の観点で問われます。",
        "定義の一文要約ができるか",
        "数値・頻度・対象者の条件を言い換えられないか",
        "関連制度（健診・教育・作業環境管理など）と混同されないか",
    ]
    for i, tip in enumerate(tips[:3], 1):
        wrong, right = parse_tip_pair(tip)
        if wrong and right:
            blocks.append(f"誤り肢の型{i}：{wrong} → {right}")
    return "；".join(blocks)


def professional_memory(term: str, category: str, tips: list[str], related: list[str]) -> str:
    lines = [
        f"■ 核心：{term}＝{CATEGORY_ANGLE.get(category, '定義＋条件')}をセットで覚える。",
    ]
    if tips:
        wrong, right = parse_tip_pair(tips[0])
        if wrong and right:
            lines.append(f"■ 誤答パターン：「{wrong[:40]}…」と見えたら → {right[:50]}…")
    if len(tips) > 1:
        _, r2 = parse_tip_pair(tips[1])
        if r2:
            lines.append(f"■ もう一つの焦点：{r2}")
    if related:
        lines.append(f"■ 比較暗記：{'・'.join(related[:3])}を表で並べ、主語がどの用語かを確認する。")
    if category == "関係法令":
        lines.append("■ 直前チェック：義務／努力／記録／選任要件の4語を頭の中で当てはめる。")
    elif category == "労働衛生":
        lines.append("■ 直前チェック：測定→評価→管理区分→措置の順で口に出してみる。")
    else:
        lines.append("■ 直前チェック：原因・症状・予防の3点を30秒で説明できるか確認する。")
    return "\n".join(lines)


def professional_lead(term: str, category: str) -> str:
    return (
        f"「{term}」を、資格試験の知識としてだけでなく、職場の安全衛生の言葉として理解できるように整理した記事です。"
        f"{EXAM_NAME}の{category}に沿って、意味・具体例・頻出の誤り・覚え方・よくある質問を順にまとめています。"
        f"初めて学ぶ方も、直前に復習する方も、段落ごとに読み進められる構成にしています。"
    )


def professional_faqs(
    term: str, category: str, summary: str, tips: list[str], related: list[str]
) -> list[tuple[str, str]]:
    wrong, right = parse_tip_pair(tips[0]) if tips else ("", "")
    faqs: list[tuple[str, str]] = [
        (
            f"{term}を学ぶうえで、最初に押さえるべきポイントは何ですか？",
            f"{summary} まずは定義を一文で言えるようにし、次に{category}の過去問で"
            f"「誰が・いつ・何をするか」に分解して読むと理解が深まります。",
        ),
        (
            f"{term}に関する過去問で、どんな“ひっかけ”が多いですか？",
            (
                f"もっとも多いのは、「{wrong}」のように正しそうな誤りです。"
                f"正解の考え方は「{right}」です。数値や頻度が1桁違う肢も要注意です。"
                if wrong and right
                else "定義は合っているが、対象者・頻度・手続きが少しずれている選択肢です。条文のイメージと照らして確認してください。"
            ),
        ),
    ]
    if related:
        faqs.append(
            (
                f"{term}と「{related[0]}」は、どう区別すればよいですか？",
                f"どちらも{category}で出題されますが、主語と役割が異なります。"
                f"本記事の関連用語と、それぞれの用語ページを並べて読むと、"
                f"「どちらの制度の話か」を瞬時に判断しやすくなります。",
            )
        )
    else:
        faqs.append(
            (
                f"{term}は独学でどの順番で復習するのが効率的ですか？",
                "①定義 ②具体例でイメージ ③誤り肢チェック ④関連用語との比較 ⑤直近の過去問。"
                "この順で10分ずつ回すと、記憶の定着率が上がります。",
            )
        )
    faqs.append(
        (
            f"現場の衛生管理者として、{term}の知識はどう活きますか？",
            f"法令・測定・健康管理の判断材料として使われます。"
            f"試験合格後も、説明・記録・改善提案の場面で同じ整理軸が役立ちます。"
            f"公式情報とあわせ、最新の要件も確認してください。",
        ),
    )
    return faqs[:4]


def enrich_glossary_row(row: dict, handmade: dict | None, related: list[str]) -> dict:
    term = (row.get("term") or "").strip()
    slug = (row.get("slug") or "").strip()
    category = (row.get("category") or "労働衛生").strip()
    base = (
        handmade.get("csv_desc") if handmade else ""
    ) or row.get("term_detail_body") or row.get("explanation") or row.get("definition") or ""
    tips = tips_from_row(row, handmade, term)

    summary = professional_summary(term, category, base, tips)
    example = professional_example(term, slug, category, tips, related)
    detail = professional_definition(term, category, base, tips)
    exam_angle = professional_exam_angle(term, category, tips)
    memory = professional_memory(term, category, tips, related)
    lead = professional_lead(term, category)
    faqs = professional_faqs(term, category, summary, tips, related)

    row["short_def"] = summary
    row["summary_example"] = example
    row["definition"] = strip_boilerplate(base)[:200]
    row["term_detail_body"] = detail
    row["explanation"] = exam_angle
    row["exam_points"] = exam_points_text(tips)
    row["common_mistakes"] = mistakes_text(tips)
    row["memory_tip"] = memory
    row["article_lead"] = lead
    for i, (q, a) in enumerate(faqs, 1):
        row[f"faq_{i}_question"] = q
        row[f"faq_{i}_answer"] = a
    return row
