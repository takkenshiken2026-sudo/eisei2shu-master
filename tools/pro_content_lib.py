"""用語詳細記事を専門家・プロライター水準の文案に整える。"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from reader_friendly_lib import (
    CONCRETE_EXAMPLES,
    concrete_example,
    exam_tips_list,
    parse_tip_pair,
    strip_boilerplate,
)

REPO = Path(__file__).resolve().parents[1]
HANDMADE = REPO / "tools" / "handmade"


def load_handmade_tips_by_slug() -> dict[str, list[str]]:
    """手作りデータから試験向け tips を取得。"""
    tips_map: dict[str, list[str]] = {}
    seen_lists: set[int] = set()
    for path in sorted(HANDMADE.glob("glossary_*_data.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(mod)
        for attr in dir(mod):
            if not attr.startswith("HANDMADE"):
                continue
            val = getattr(mod, attr)
            if not isinstance(val, list) or not val or not isinstance(val[0], dict):
                continue
            lid = id(val)
            if lid in seen_lists:
                continue
            seen_lists.add(lid)
            for item in val:
                slug = item.get("slug", "")
                if not slug:
                    continue
                sects = item.get("sections") or []
                tips: list[str] = []
                for title, body in sects:
                    if title == "試験で狙われる頻出ポイント" and isinstance(body, list):
                        tips = [str(x) for x in body]
                if tips:
                    tips_map[slug] = tips
    return tips_map


def normalize_tip(tip: str) -> str:
    tip = tip.strip()
    tip = re.sub(r"^誤[：:]\s*", "", tip)
    tip = re.sub(r"^正[：:]\s*", "", tip)
    return tip


def tips_from_row(row: dict, handmade: dict[str, list[str]]) -> list[str]:
    slug = (row.get("slug") or "").strip()
    if slug in handmade:
        return handmade[slug][:4]
    return exam_tips_list(row.get("exam_points", ""), row.get("common_mistakes", ""))[:4]


def expert_short_def(term: str, category: str, core: str) -> str:
    core = strip_boilerplate(core)
    if len(core) > 110:
        core = core[:107] + "…"
    return (
        f"「{term}」は、第二種衛生管理者試験の{category}で繰り返し問われるキーワードです。"
        f"{core}"
    )


def expert_summary_example(term: str, slug: str, category: str, tips: list[str], related: list[str]) -> str:
    if slug in CONCRETE_EXAMPLES:
        return CONCRETE_EXAMPLES[slug].replace("【具体例】", "").strip()
    return concrete_example(term, slug, category, tips, related).replace("【具体例】", "").strip()


def expert_detail_body(term: str, category: str, core: str, tips: list[str], related: list[str]) -> str:
    core = strip_boilerplate(core)
    parts = [
        f"{term}は、職場の安全衛生管理や試験の{category}分野で欠かせない概念です。"
        f"{core}",
    ]
    if tips:
        w, r = parse_tip_pair(tips[0])
        if r:
            parts.append(
                f"過去問では「{w.strip('「」 ')}」のように聞こえる選択肢が混ざることがあります。"
                f"正しくは、{r}という整理で判断します。"
            )
    if len(tips) > 1:
        _, r2 = parse_tip_pair(tips[1])
        if r2:
            parts.append(f"あわせて、{r2}という点もセットで押さえておきましょう。")
    if related:
        parts.append(
            f"理解を深めるには、「{related[0]}」"
            + (f"「{related[1]}」" if len(related) > 1 else "")
            + "との違いを表にまとめて比較するのが効果的です。"
        )
    return "\n\n".join(parts)


def expert_exam_points(tips: list[str]) -> str:
    lines: list[str] = []
    for tip in tips[:4]:
        w, r = parse_tip_pair(normalize_tip(tip))
        if w and r:
            lines.append(f"{w.strip('「」 ')}と捉えがちですが、{r}。")
        elif tip:
            lines.append(tip.rstrip("。") + "。")
    return "；".join(lines)


def expert_common_mistakes(tips: list[str]) -> str:
    lines: list[str] = []
    for tip in tips[:3]:
        w, r = parse_tip_pair(normalize_tip(tip))
        if not w:
            continue
        w = w.strip("「」 ").lstrip("誤").strip("：: ")
        r = r.strip() if r else "条文・数値・手順で確認"
        lines.append(f"× {w}\n→ {r}")
    return "\n\n".join(lines)


def expert_memory_tip(term: str, category: str, tips: list[str], related: list[str]) -> str:
    lines = [
        f"■ 核心：{term}は「定義＋数値・主体・記録」のどれを問うかを先に見極める。",
    ]
    if tips:
        w, r = parse_tip_pair(tips[0])
        if w and r:
            lines.append(f"■ ひっかけ：「{w.strip('「」 ')}」→ 正しくは「{r[:40]}…」" if len(r) > 40 else f"■ ひっかけ：「{w.strip('「」 ')}」→ 正しくは「{r}」")
    if category == "関係法令":
        lines.append("■ 暗記順：①義務の有無 → ②誰が実施 → ③いつ・頻度 → ④記録保存 → ⑤違反時の措置。")
    elif category == "労働衛生":
        lines.append("■ 暗記順：①測定の目的 → ②方式・単位 → ③評価基準 → ④改善・保護具 → ⑤記録。")
    else:
        lines.append("■ 暗記順：①定義 → ②原因・経路 → ③症状・影響 → ④予防・管理措置。")
    if related:
        lines.append(f"■ 関連語セット：{'・'.join(related[:3])}（表で横並び比較）。")
    lines.append("■ 直前確認：過去問で「主語」と「数値の単位」を声に出してチェック。")
    return "\n".join(lines)


def expert_article_lead(term: str, category: str) -> str:
    return (
        f"本記事は、第二種衛生管理者試験の受験者向けに「{term}」を専門的かつ分かりやすく解説した用語ガイドです。"
        f"{category}の過去問で問われる定義・数値・誤り肢を、具体例と覚え方つきで整理しています。"
        f"初めて学ぶ方も、直前に復習する方も、このページだけで要点を押さえられる構成にしました。"
    )


def expert_faqs(
    term: str,
    category: str,
    short_def: str,
    detail: str,
    tips: list[str],
    related: list[str],
) -> list[tuple[str, str]]:
    w, r = parse_tip_pair(tips[0]) if tips else ("", "")
    faqs: list[tuple[str, str]] = [
        (
            f"「{term}」を一言で言うと、現場では何のために必要ですか？",
            f"{short_def} 試験では定義の暗記だけでなく、"
            f"事業者・衛生管理者・産業医のどの役割に関わるかまで問われることがあります。",
        ),
        (
            f"第二種衛生管理者試験で「{term}」はどのように出題されますか？",
            (
                f"{category}の選択肢では、"
                f"「{w.strip('「」 ')}」のような言い換えが頻出です。"
                f"正解は「{r}」の考え方に沿っているかを確認する練習を重ねましょう。"
                if w and r
                else f"{category}では、定義・数値・手続きの言い換えを見抜く問題が中心です。"
            ),
        ),
    ]
    if related:
        faqs.append(
            (
                f"「{term}」と「{related[0]}」は何が違いますか？",
                f"名称が似ていると混同しやすい組み合わせです。"
                f"{term}は主に{category}の文脈で、{related[0]}は別の観点（測定・措置・制度）を担うことが多いです。"
                f"本文の関連用語と過去問を並べて復習してください。",
            )
        )
    else:
        faqs.append(
            (
                f"「{term}」の覚え方でおすすめの方法は？",
                "キーワードカードに「定義／数値／主体／記録」を書き、"
                "関連する法令名や規則名を裏面に書くと定着率が上がります。",
            )
        )
    faqs.append(
        (
            f"受験直前に「{term}」で最後に見るべきポイントは？",
            "①定義を自分の言葉で説明できるか ②頻出の誤り肢 ③関連する数値・単位。"
            "本記事の「試験で押さえるポイント」とリンク先の過去問で、選択肢形式に慣れておきましょう。",
        )
    )
    return faqs[:4]
