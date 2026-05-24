"""用語詳細記事をやさしく読みやすい文体に整えるヘルパ。"""
from __future__ import annotations

import re

# 試験用語として頻出の具体例（スラッグ別）
CONCRETE_EXAMPLES: dict[str, str] = {
    "wbgt": (
        "【具体例】真夏の屋外で舗装作業をするとき、気温だけでなく日射と湿度も暑さに影響します。"
        "WBGTは、湿球・黒球・乾球の値から「その場の暑さ」を一つの指数にまとめ、"
        "熱中症のリスクが高いかどうかを判断する目安に使います。"
    ),
    "rodo-anzen-eisei-ho": (
        "【具体例】ある工場で労災が起きたあと、監督署から「安全衛生管理体制は整っているか」"
        "と聞かれる場面を想像してください。労働安全衛生法は、事業者に衛生管理者の選任や"
        "健康診断、教育などを求める“土台”となる法律です。"
    ),
    "sanso-ketsubosho": (
        "【具体例】タンクの内部清掃やマンホール内作業では、酸素が欠けると意識障害や死亡事故につながります。"
        "酸素濃度18%未満の場所への立入禁止や、測定・換気・監視人の配置が、酸素欠乏症防止の中心です。"
    ),
    "kyokuho-haikisochi": (
        "【具体例】溶剤を使う塗装作業では、作業者の呼吸域に蒸気が広がりやすくなります。"
        "局所排気装置は、発生源の近くで汚染空気を吸い込み、作業場全体を汚さないための装置です。"
    ),
    "teiki-kenko-shindan": (
        "【具体例】4月に入社した正社員は、雇入れ時健診のあと、毎年1回の定期健診の対象になります。"
        "「パートは対象外」「入社後1か月以内ならよい」といった言い換えが、定期健診まわりでよく出ます。"
    ),
    "eisei-kanrisha": (
        "【具体例】常時50人以上の製造業では、第一種または第二種の衛生管理者を選任し、"
        "作業環境の改善や健康診断結果の管理などを任せます。産業医や安全管理者とは役割が異なります。"
    ),
    "kishuu": (
        "【具体例】粉じん作業場では、決められた流量で空気を吸引し、ろ過材に粒子を捕集して"
        "後から分析します。測定の直前にポンプの流量を合わせる「流量校正」が、気集の基本手順です。"
    ),
}


def strip_boilerplate(text: str) -> str:
    text = (text or "").strip()
    for phrase in (
        "試験では数値・手順・誤り肢を本文表と合わせて確認してください。",
        "出題では",
        "第二種試験では名称より、",
    ):
        if phrase in text:
            idx = text.find(phrase)
            if idx > 20:
                text = text[:idx].strip()
    text = re.sub(r"\s+", " ", text)
    return text.rstrip("。") + "。" if text and not text.endswith("。") else text


def simplify_sentence(text: str) -> str:
    text = strip_boilerplate(text)
    repl = (
        ("であります", "です"),
        ("となります", "になります"),
        ("することができます", "できます"),
        ("することが求められます", "が求められます"),
        ("いうものです", "という考え方です"),
        ("いうことです", "ということです"),
        ("に関する", "についての"),
    )
    for old, new in repl:
        text = text.replace(old, new)
    return text


def exam_tips_list(exam_points: str, common_mistakes: str) -> list[str]:
    tips: list[str] = []
    for blob in (exam_points, common_mistakes):
        for part in re.split(r"[;；\n]", blob or ""):
            part = part.strip()
            if part and part not in tips:
                tips.append(part)
    return tips[:4]


def parse_tip_pair(tip: str) -> tuple[str, str]:
    if "→" in tip:
        left, right = tip.split("→", 1)
        return left.strip("「」 "), right.strip()
    return tip, ""


def concrete_example(
    term: str,
    slug: str,
    category: str,
    tips: list[str],
    related: list[str],
) -> str:
    if slug in CONCRETE_EXAMPLES:
        return CONCRETE_EXAMPLES[slug]
    wrong, right = parse_tip_pair(tips[0]) if tips else ("", "")
    rel = related[0] if related else ""
    if category == "関係法令":
        return (
            f"【具体例】ある事業場で「{term}」が問われるとします。"
            f"過去問では、{wrong or '義務がない・記録不要'}のように聞こえる選択肢が混ざります。"
            f"正しくは、{right or '誰が・いつ・何を記録するかを法令どおりに行うか'}を確認する問題です。"
            + (f"「{rel}」とあわせて覚えると整理しやすくなります。" if rel else "")
        )
    if category == "労働衛生":
        return (
            f"【具体例】作業環境測定や保護具の場面で「{term}」が出てきます。"
            f"数値や手順だけを暗記するのではなく、"
            f"{right or '測定の目的と現場での使い方'}をイメージして選ぶと理解が定着します。"
            + (f"関連する「{rel}」も同時に確認しておくとよいです。" if rel else "")
        )
    return (
        f"【具体例】{category}では、{term}を体のしくみや環境の影響と結びつけて問われます。"
        f"{right or '症状・原因・対策をセットで覚える'}と、選択肢の言い換えに強くなります。"
        + (f"「{rel}」と比較する問題も出やすいです。" if rel else "")
    )


def plain_short_def(term: str, category: str, base: str) -> str:
    core = simplify_sentence(base)
    if core.startswith(term) or core.startswith(f"「{term}"):
        lead = f"これは{category}でよく出る用語です。"
    else:
        lead = f"「{term}」は、{category}で押さえるキーワードです。"
    if len(core) > 130:
        core = core[:127] + "…"
    return f"{lead}{core}"


def plain_definition(term: str, category: str, detail: str, tips: list[str]) -> str:
    parts = [simplify_sentence(detail)]
    if tips:
        _, right = parse_tip_pair(tips[0])
        if right:
            parts.append(f"試験では特に、「{right}」という整理が重要です。")
    return " ".join(parts)


def memory_tip_detailed(
    term: str,
    category: str,
    tips: list[str],
    related: list[str],
) -> str:
    lines: list[str] = []
    lines.append(
        f"■ ひとことで：{term}は「何を・誰が・いつ」がセットで問われる{category}の用語です。"
    )
    if tips:
        wrong, right = parse_tip_pair(tips[0])
        if wrong and right:
            lines.append(f"■ 誤り肢の見方：「{wrong}」と書かれていたら、{right}かを疑う。")
    if len(tips) > 1:
        _, right2 = parse_tip_pair(tips[1])
        if right2:
            lines.append(f"■ もう一つの焦点：{right2}")
    if related:
        lines.append(
            "■ セットで整理："
            + "・".join(related[:3])
            + "。似た用語と表で比較すると記憶に残ります。"
        )
    if category == "関係法令":
        lines.append("■ 暗記の順番：①義務の有無 → ②実施主体 → ③記録・保存 → ④違反時の措置。")
    elif category == "労働衛生":
        lines.append("■ 暗記の順番：①測定・評価の目的 → ②数値・単位 → ③改善・保護具 → ④記録。")
    else:
        lines.append("■ 暗記の順番：①定義 → ②原因・経路 → ③症状 → ④予防・管理。")
    return "\n".join(lines)


def build_faqs(
    term: str,
    category: str,
    short_def: str,
    tips: list[str],
    related: list[str],
) -> list[tuple[str, str]]:
    wrong, right = parse_tip_pair(tips[0]) if tips else ("", "")
    faqs: list[tuple[str, str]] = [
        (
            f"{term}とは、何のために学ぶ用語ですか？",
            f"{short_def} 試験では「意味を知っているか」より、"
            f"現場や法令の場面でどう使われるかが問われます。",
        ),
        (
            f"{term}は、試験でどんな出題形式になりやすいですか？",
            (
                f"{category}では、定義の確認に加え、"
                f"「{wrong}」のような誤り選択肢を正しい説明と見比べる問題が多いです。"
                if wrong
                else f"{category}では、定義・数値・手順の言い換えを見抜く問題が中心です。"
            ),
        ),
    ]
    if related:
        faqs.append(
            (
                f"{term}と「{related[0]}」の違いは何ですか？",
                f"両方とも{category}で出ますが、役割が異なります。"
                f"本文の表と関連用語リンクで並べて比較し、"
                f"過去問ではどちらの用語が主語かに注意してください。",
            )
        )
    else:
        faqs.append(
            (
                f"{term}を覚えるときのコツはありますか？",
                "長文を一気に暗記するより、"
                "「誰が・いつ・何をするか」または「測定→評価→措置」の流れに分解すると復習しやすくなります。",
            )
        )
    faqs.append(
        (
            f"受験直前に{term}で最終確認すべき点は？",
            (
                f"①{right or '定義の一言'} ②頻出の誤り肢 ③関連する制度・数値。"
                "本記事の「試験で押さえるポイント」と過去問リンクで確認してください。"
            ),
        )
    )
    return faqs[:4]


def plain_article_lead(term: str, category: str, short_def: str) -> str:
    return (
        f"このページでは、{term}の意味をやさしい言葉で説明し、"
        f"{category}の過去問で問われやすいポイントを具体例つきで整理します。"
        f"初めて読む方でも、試験勉強の復習としても使える構成にしています。"
    )
