#!/usr/bin/env python3
"""第4弾50語の記事本文・CSV（exam_points / common_mistakes）を充実させる。"""
from __future__ import annotations

import csv
import importlib.util
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTICLES = REPO / "eisei-articles" / "articles"
GLOSSARY_CSV = REPO / "data" / "glossary_terms.csv"

_spec = importlib.util.spec_from_file_location(
    "batch4", REPO / "tools" / "add_50_glossary_articles_batch4.py"
)
_batch4 = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_batch4)

_spec1 = importlib.util.spec_from_file_location(
    "batch1", REPO / "tools" / "add_35_glossary_articles.py"
)
_batch1 = importlib.util.module_from_spec(_spec1)
assert _spec1.loader
_spec1.loader.exec_module(_batch1)

build_body = _batch1.build_body
render_section = _batch1.render_section
NEW_TERMS = _batch4.NEW_TERMS

# デフォルトセクションのみの用語向け・試験頻出の誤り選択肢
DEFAULT_EXAM_TIPS: dict[str, list[str]] = {
    "定期健康診断": [
        "「パートタイムは対象外」→ 常時使用する労働者に含める",
        "「2年に1回でよい」→ 1年以内ごとに1回",
        "「雇入れ後1か月以内で実施すればよい」→ 就業前が原則",
    ],
    "面接指導": [
        "「衛生管理者が面接指導を行う」→ 産業医（医師）が実施",
        "「長時間労働者面接指導と同じ対象・条件」→ 別制度として整理",
    ],
    "一次健康診断": [
        "「一次健診で異常があっても二次健診は任意」→ 所見に応じ二次健診・措置",
        "「一次＝特殊健康診断」→ 定期健診の最初の段階",
    ],
    "労働基準監督署": [
        "「労働安全衛生の監督は厚労省のみ」→ 労基署も職権を持つ場面がある",
    ],
    "労働衛生コンサルタント": [
        "「衛生管理者と同一資格」→ 別資格・助言・測定等の専門家",
    ],
    "免許": [
        "「試験合格＝即免許」→ 申請・交付の手続きがある",
    ],
    "安全衛生委員会": [
        "「衛生委員会があれば安全衛生委員会は不要」→ 要件は別",
    ],
    "化学物質": [
        "「SDSがあればリスクアセスメント不要」→ 両方が管理の柱",
    ],
    "時間外労働": [
        "「時間外＝長時間労働（同一概念）」→ 長時間労働は一定時間超の状態",
    ],
    "副交感神経": [
        "「心拍を増加させる」→ 交感神経の作用",
        "「消化管運動を抑制する」→ 副交感神経は亢進",
    ],
    "自律神経": [
        "「随意筋を支配する」→ 体性神経",
    ],
    "体性神経": [
        "「内臓の機能を調節する」→ 自律神経",
    ],
    "神経核": [
        "「神経核は末梢神経系」→ 中枢神経系（脳・脊髄）",
        "「神経節と神経核は同じ」→ 神経核＝中枢、神経節＝末梢",
    ],
    "神経節": [
        "「神経節は中枢神経系」→ 末梢神経系",
    ],
    "不顕性感染": [
        "「抵抗力低下時の発症＝不顕性感染」→ 日和見感染の説明",
        "「無症状＝感染未成立」→ 不顕性は感染成立・症状なし",
    ],
    "中枢神経系": [
        "「末梢神経系は脳と脊髄からなる」→ 中枢神経系",
    ],
    "末梢神経系": [
        "「神経核は末梢に位置する」→ 神経核は中枢",
    ],
    "日和見感染": [
        "「症状が出ない感染＝不顕性感染の説明」→ 日和見は抵抗力低下時の発症",
    ],
    "キャリア": [
        "「必ず発熱する」→ 無症状で病原体を散布しうる",
    ],
    "飛沫感染": [
        "「5µm以下の粒子が長時間浮遊＝飛沫感染」→ 空気感染",
    ],
    "空気感染": [
        "「大きな飛沫のみが空気感染」→ 小粒子の浮遊が特徴",
    ],
    "接触感染": [
        "「空気中の粒子吸入のみ」→ 付着物への接触",
    ],
    "感染症": [
        "「病原体がなくても感染成立」→ 病原体・宿主・感染経路が必要",
    ],
    "病原体": [
        "「ウイルス以外は病原体ではない」→ 細菌・真菌等も含む",
    ],
    "二酸化炭素": [
        "「二酸化炭素は有毒ガスで酸素欠乏の主因」→ 換気不良で濃度上昇し酸素欠乏の一因",
    ],
    "一酸化炭素": [
        "「二酸化炭素と同様に窒息の主因」→ ヘモグロビン結合で酸素運搬阻害",
    ],
    "不感蒸泄": [
        "「発汗のみが熱放散」→ 不感蒸泄も重要",
    ],
    "発汗": [
        "「汗をかかない環境では体温上昇しない」→ 不感蒸泄もある",
    ],
    "代謝率": [
        "「代謝率とWBGTは無関係」→ 温熱環境評価に用いる",
    ],
    "大脳": [
        "「平衡機能は大脳皮質の主機能」→ 小脳",
    ],
    "小脳": [
        "「思考・言語は小脳の主機能」→ 大脳皮質",
    ],
    "粉じん": [
        "「粉じん＝アスベストのみ」→ 鉱物性・有機性など多様",
    ],
    "硫化水素": [
        "「無臭で有害」→ 悪臭（腐卵臭）がある",
    ],
    "アンモニア": [
        "「慢性毒性のみ」→ 強い刺激性",
    ],
    "塩素": [
        "「可燃性ガス」→ 刺激性・酸化性",
    ],
    "有機リン": [
        "「胆碱酯酶を活性化する」→ 阻害",
    ],
    "水銀": [
        "「金属水銀は経口吸収が主」→ 蒸気・皮膚等のばく露経路に注意",
    ],
    "石綿": [
        "「石綿は急性毒性が主」→ 長期ばく露で肺がん・間皮腫等",
    ],
    "シリカ": [
        "「シリカは有機粉じん」→ 結晶質シリカはじん肺の原因",
    ],
    "減圧症": [
        "「高気圧作業で増圧のみ問題」→ 減圧の速さが重要",
    ],
    "急性毒性": [
        "「長期ばく露で現れる」→ 慢性毒性",
    ],
    "慢性毒性": [
        "「短期間のばく露で現れる」→ 急性毒性",
    ],
    "血中": [
        "「尿中のみが生物学的モニタリング」→ 血中・尿中など",
    ],
    "尿中": [
        "「作業環境測定と同じ意味」→ 生体試料によるばく露評価",
    ],
    "血中濃度": [
        "「管理濃度と同じ指標」→ 作業環境と生体試料は別",
    ],
    "騒音": [
        "「騒音＝音の大きさのみ、周波数無関係」→ A特性補正等で評価",
    ],
    "作業環境管理": [
        "「測定のみで終了」→ 評価・改善・記録の流れ",
    ],
    "ばく露": [
        "「ばく露＝作業環境濃度のみ」→ 個人ばく露評価もある",
    ],
}


def sections_with_tips(item: dict) -> list:
    sections = list(item.get("sections") or [])
    tips = []
    for h2, content in sections:
        if h2 in ("試験で狙われる頻出ポイント", "試験での注意点"):
            if isinstance(content, list):
                for row in content:
                    if isinstance(row, str):
                        tips.append(row)
    extra = DEFAULT_EXAM_TIPS.get(item["term"], [])
    if extra:
        has_tip_section = any(h in ("試験で狙われる頻出ポイント", "試験での注意点") for h, _ in sections)
        if not has_tip_section:
            sections.append(("試験で狙われる頻出ポイント", extra))
        else:
            # merge into existing bullet section
            for i, (h2, content) in enumerate(sections):
                if h2 in ("試験で狙われる頻出ポイント", "試験での注意点"):
                    merged = list(content) if isinstance(content, list) else []
                    for e in extra:
                        if e not in merged:
                            merged.append(e)
                    sections[i] = (h2, merged)
                    break
        tips.extend(extra)
    return sections, tips


def exam_points_csv(tips: list[str]) -> str:
    cleaned = []
    for t in tips:
        t = re.sub(r"^[「『]", "", t.strip())
        t = re.sub(r"」→.*$", "", t)
        t = re.sub(r"→.*$", "", t).strip()
        if t and t not in cleaned:
            cleaned.append(t)
    return ";".join(cleaned[:6])


def common_mistakes_text(tips: list[str]) -> str:
    mistakes = [t for t in tips if "→" in t or "誤り" in t]
    if not mistakes:
        return ""
    return " ".join(mistakes[:3])


def patch_markdown(item: dict, sections: list) -> None:
    md_path = ARTICLES / f"{item['file']}.md"
    if not md_path.is_file():
        return
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return
    parts = text.split("---", 2)
    if len(parts) < 3:
        return
    body = build_body(item["term"], item["title"], item["category"], sections)
    md_path.write_text(parts[0] + "---" + parts[1] + "---\n\n" + body, encoding="utf-8")


def update_csv(items: list[dict], tips_by_term: dict[str, list[str]]) -> int:
    with GLOSSARY_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    slugs = {item["slug"] for item in items}
    updated = 0
    for row in rows:
        if row.get("slug") not in slugs:
            continue
        tips = tips_by_term.get(row["term"], [])
        ep = exam_points_csv(tips)
        cm = common_mistakes_text(tips)
        if ep:
            row["exam_points"] = ep
        if cm:
            row["common_mistakes"] = cm
        row["term_detail_body"] = row.get("definition") or row.get("short_def") or ""
        updated += 1
    with GLOSSARY_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return updated


def main() -> None:
    tips_by_term: dict[str, list[str]] = {}
    for item in NEW_TERMS:
        sections, tips = sections_with_tips(item)
        tips_by_term[item["term"]] = tips
        patch_markdown(item, sections)
        print(f"enriched md: {item['file']}.md")

    n = update_csv(NEW_TERMS, tips_by_term)
    print(f"updated csv rows: {n}")


if __name__ == "__main__":
    main()
