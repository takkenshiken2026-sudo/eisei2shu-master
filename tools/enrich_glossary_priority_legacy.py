#!/usr/bin/env python3
"""既存用語（第1〜3弾）のうち試験頻出・本文薄い語を優先して exam_points / 本文を充実。"""
from __future__ import annotations

import csv
import importlib.util
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTICLES = REPO / "eisei-articles" / "articles"
GLOSSARY_CSV = REPO / "data" / "glossary_terms.csv"
SLUG_JSON = REPO / "docs" / "glossary-article-slugs.json"

_spec1 = importlib.util.spec_from_file_location(
    "batch1", REPO / "tools" / "add_35_glossary_articles.py"
)
_batch1 = importlib.util.module_from_spec(_spec1)
assert _spec1.loader
_spec1.loader.exec_module(_batch1)
build_body = _batch1.build_body
render_section = _batch1.render_section

_spec4 = importlib.util.spec_from_file_location(
    "enrich4", REPO / "tools" / "enrich_batch4_glossary.py"
)
_enrich4 = importlib.util.module_from_spec(_spec4)
assert _spec4.loader
_spec4.loader.exec_module(_enrich4)
sections_with_tips = _enrich4.sections_with_tips
exam_points_csv = _enrich4.exam_points_csv
common_mistakes_text = _enrich4.common_mistakes_text
DEFAULT_EXAM_TIPS = _enrich4.DEFAULT_EXAM_TIPS

_spec_b4 = importlib.util.spec_from_file_location(
    "batch4", REPO / "tools" / "add_50_glossary_articles_batch4.py"
)
_batch4 = importlib.util.module_from_spec(_spec_b4)
assert _spec_b4.loader
_spec_b4.loader.exec_module(_batch4)
csv_row = _batch4.csv_row

# チェックリスト・過去問頻出の既存用語（slug は glossary_terms.csv に合わせる）
PRIORITY: list[dict] = [
    {
        "term": "検知管",
        "slug": "kenchi-kan",
        "category": "労働衛生",
        "title": "検知管とは？直接読み取り式測定・簡易測定",
        "csv_desc": "ガス濃度を簡易に測る直接読み取り式の器具です。捕集分析法との使い分けが出ます。",
        "sections": [
            ("検知管の特徴", [
                ["項目", "内容"],
                ["方式", "直接読み取り式（その場で色変化等）"],
                ["用途", "簡易確認・トレーサビリティの補助"],
                ["限界", "物質・濃度域は種類により限定"],
            ]),
            ("捕集分析法との違い", [
                ["項目", "検知管", "捕集分析法"],
                ["分析", "その場で目安", "試料を捕集し後分析"],
                ["精度", "簡易", "法令上の作業環境測定の主方式"],
            ]),
            ("試験で狙われる頻出ポイント", [
                "「検知管だけで作業環境測定が完了」→ 捕集分析法が基本",
                "「検知管の結果で管理区分を決定」→ 正式測定・評価の流れを確認",
            ]),
        ],
    },
    {
        "term": "気集",
        "slug": "kishuu",
        "category": "労働衛生",
        "title": "気集とは？吸引採取・作業環境測定・流量校正",
        "csv_desc": "空気中の粒子を決められた条件で試料として採取する作業です。",
        "sections": [
            ("気集の手順の要点", [
                ["手順", "内容"],
                ["流量校正", "測定前にポンプ流量を確認"],
                ["吸引採取", "決められた時間・流量で採取"],
                ["分析", "捕集材を分析して濃度算出"],
            ]),
            ("試験で狙われる頻出ポイント", [
                "「流量校正は測定後でよい」→ 採取前が原則",
                "「気集＝ガス状物質のみ」→ 粉じん等の粒子採取",
            ]),
        ],
    },
    {
        "term": "許容濃度",
        "slug": "kyoyou-noudo-standalone",
        "category": "労働衛生",
        "title": "許容濃度とは？管理濃度・測定結果の評価",
        "csv_desc": "作業環境の濃度目安となる指標です。管理濃度等と混同しやすい。",
        "sections": [
            ("許容濃度と管理濃度", [
                ["項目", "許容濃度（の考え方）", "管理濃度"],
                ["位置づけ", "目安・指標", "法令上の管理の基準"],
                ["試験", "言い換えに注意", "作業環境管理区分と関連"],
            ]),
            ("試験で狙われる頻出ポイント", [
                "「許容濃度＝管理濃度と同じ」→ 制度上の呼び方・使われ方を整理",
                "「超えても直ちに作業停止」→ 評価・改善の流れで判断",
            ]),
        ],
    },
    {
        "term": "特別有機溶剤等",
        "slug": "tokubetsu-yuki-yozai",
        "category": "関係法令",
        "title": "特別有機溶剤等とは？区分・義務・局所排気",
        "csv_desc": "有機溶剤のうち特に厳しい管理が求められる区分です。",
        "sections": [
            ("有機溶剤の区分", [
                ["区分", "義務のイメージ"],
                ["特別有機溶剤等", "最も厳しい"],
                ["第1種有機溶剤等", "厳しい"],
                ["第2種有機溶剤等", "比較的緩い"],
            ]),
            ("試験で狙われる頻出ポイント", [
                "「第1種と特別は同じ」→ 名称と義務セットを区別",
                "「区分が緩いほど局所排気不要」→ 区分ごとに確認",
            ]),
        ],
    },
    {
        "term": "安全衛生教育",
        "slug": "anzen-eisei-kyoiku",
        "category": "関係法令",
        "title": "安全衛生教育とは？対象・時間・記録",
        "csv_desc": "職種・作業に応じた安全衛生の教育です。特別教育との違いが頻出。",
        "sections": [
            ("教育の種類", [
                ["種類", "主な対象"],
                ["安全衛生教育", "新規雇入れ・職種変更等"],
                ["特別教育", "危険有害作業"],
                ["職長等教育", "職長・班長等"],
            ]),
            ("試験で狙われる頻出ポイント", [
                "「特別教育＝安全衛生教育」→ 対象・実施時期が異なる",
                "「教育の記録保存不要」→ 記録・保存期間を確認",
            ]),
        ],
    },
    {
        "term": "作業環境評価",
        "slug": "sagyo-kankyo-hyoka",
        "category": "労働衛生",
        "title": "作業環境評価とは？管理区分・測定後の流れ",
        "csv_desc": "測定結果から作業環境の管理区分を判定する流れです。",
        "sections": [
            ("測定から評価まで", [
                ["段階", "内容"],
                ["測定", "決められた方法で実施"],
                ["評価", "管理区分の判定"],
                ["改善", "区分に応じた対策・再測定"],
            ]),
            ("試験で狙われる頻出ポイント", [
                "「測定＝評価で終了」→ 記録・表示・改善へ",
                "「第3管理区分は測定不要」→ 区分ごとの義務を確認",
            ]),
        ],
    },
    {
        "term": "直接読み取り式測定",
        "slug": "chokusetsu-yomitori-sokutei",
        "category": "労働衛生",
        "title": "直接読み取り式測定とは？検知管・捕集分析法との違い",
        "csv_desc": "その場で濃度を読み取る測定方式です。",
        "sections": [
            ("方式の比較", [
                ["方式", "特徴"],
                ["直接読み取り式", "即時・簡易"],
                ["捕集分析法", "試料採取・後分析（正式測定の中心）"],
            ]),
            ("試験で狙われる頻出ポイント", [
                "「直接読み取りのみで法令測定完結」→ 捕集分析法が基本",
            ]),
        ],
    },
    {
        "term": "置換換気",
        "slug": "chikan-kanki",
        "category": "労働衛生",
        "title": "置換換気とは？全面換気・希釈換気との違い",
        "csv_desc": "きれいな空気で汚染空気を置き換える換気方式です。",
        "sections": [
            ("換気方式の整理", [
                ["方式", "イメージ"],
                ["局所排気", "発生源で捕集"],
                ["置換換気", "きれいな空気で置換"],
                ["希釈換気", "全体を薄める"],
            ]),
            ("試験で狙われる頻出ポイント", [
                "「置換換気があれば局所排気不要」→ 発生源対策は局所が基本",
            ]),
        ],
    },
    {
        "term": "ミゼットインピンジャー",
        "slug": "mizetto-inpinja",
        "category": "労働衛生",
        "title": "ミゼットインピンジャーとは？液捕集・ガス測定",
        "csv_desc": "ガス・蒸気を液体に吸収して捕集する器具です。",
        "sections": [
            ("試験で狙われる頻出ポイント", [
                "「粉じん採取に使用」→ ガス・蒸気の液捕集",
                "「捕集液は何でもよい」→ 対象物質に応じて選定",
            ]),
        ],
    },
    {
        "term": "パッシブサンプラー",
        "slug": "passive-sampler",
        "category": "労働衛生",
        "title": "パッシブサンプラーとは？拡散採取・個人ばく露",
        "csv_desc": "拡散で試料を採取する方法・器具です。",
        "sections": [
            ("試験で狙われる頻出ポイント", [
                "「ポンプ吸引が必須」→ 拡散による採取",
                "「個人サンプリングに使えない」→ 個人ばく露評価に用いる場面がある",
            ]),
        ],
    },
]


def find_md_by_slug(slug: str) -> Path | None:
    for p in ARTICLES.glob("*.md"):
        text = p.read_text(encoding="utf-8")
        if f"slug: {slug}" in text or f"slug: {slug}\n" in text:
            return p
    # fallback: slug map reverse + filename pattern
    for p in ARTICLES.glob(f"*{slug}*.md"):
        return p
    for p in ARTICLES.glob("*.md"):
        if p.stem.endswith(slug) or slug in p.stem:
            return p
    return None


def patch_md(item: dict, sections: list) -> bool:
    md = find_md_by_slug(item["slug"])
    if not md:
        return False
    text = md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False
    parts = text.split("---", 2)
    body = build_body(item["term"], item["title"], item["category"], sections)
    md.write_text(parts[0] + "---" + parts[1] + "---\n\n" + body, encoding="utf-8")
    return True


def update_csv_row(term: str, slug: str, tips: list[str], csv_desc: str) -> bool:
    with GLOSSARY_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    hit = False
    for row in rows:
        if row.get("term") != term and row.get("slug") != slug:
            continue
        hit = True
        ep = exam_points_csv(tips)
        cm = common_mistakes_text(tips)
        if ep:
            row["exam_points"] = ep
        if cm:
            row["common_mistakes"] = cm
        if csv_desc:
            row["short_def"] = csv_desc
            row["definition"] = csv_desc
            row["explanation"] = csv_desc
        break
    if not hit:
        return False
    with GLOSSARY_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return True


def create_missing_kishuu(item: dict) -> None:
    """チェックリストのみ存在していた「気集」を新規追加。"""
    import json

    slug = item["slug"]
    slug_map = json.loads(SLUG_JSON.read_text(encoding="utf-8"))
    if item["term"] in slug_map or slug in slug_map.values():
        return
    order = 267
    file_stem = f"{order}-kishuu"
    fm = _batch1.build_frontmatter(
        {
            "order": order,
            "term": item["term"],
            "slug": slug,
            "category": item["category"],
            "title": item["title"],
            "related": "kyuin-saishu:吸引採取;hoshu-bunseki-ho:捕集分析法;ryuryo-kosei:流量計の校正",
            "intent": "気集の手順と流量校正の重要性を理解すること。",
        }
    ).replace("用語35本追加バッチ", "用語チェックリスト優先追加")
    sections, _ = sections_with_tips(item)
    body = build_body(item["term"], item["title"], item["category"], sections)
    (ARTICLES / f"{file_stem}.md").write_text(fm + "\n\n" + body, encoding="utf-8")
    slug_map[item["term"]] = slug
    SLUG_JSON.write_text(json.dumps(slug_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    row = csv_row(
        {
            "term": item["term"],
            "slug": slug,
            "category": item["category"],
            "title": item["title"],
            "csv_desc": item["csv_desc"],
            "related_terms_csv": "吸引採取;捕集分析法;流量計の校正",
        }
    )
    with GLOSSARY_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    rows.append(row)
    with GLOSSARY_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"created new: {item['term']}")


def main() -> None:
    create_missing_kishuu(next(i for i in PRIORITY if i["term"] == "気集"))
    md_ok = csv_ok = 0
    for item in PRIORITY:
        sections, tips = sections_with_tips(item)
        if patch_md(item, sections):
            md_ok += 1
            print(f"md: {item['term']}")
        else:
            print(f"skip md (no file): {item['term']} ({item['slug']})")
        # CSV は用語名で一致（複合用語は別途）
        if update_csv_row(item["term"], item["slug"], tips, item["csv_desc"]):
            csv_ok += 1
            print(f"csv: {item['term']}")
        elif item["term"] == "許容濃度":
            if update_csv_row("許容濃度・管理濃度", "kyoyo-nodo", tips, item["csv_desc"]):
                csv_ok += 1
                print("csv: 許容濃度・管理濃度")
        elif item["term"] == "特別有機溶剤等":
            if update_csv_row(
                "特別有機溶剤等・第1種・第2種有機溶剤等の区分",
                "yuki-yozai-kubun",
                tips,
                item["csv_desc"],
            ):
                csv_ok += 1
                print("csv: 特別有機溶剤等（複合用語）")
    print(f"done: md={md_ok}, csv={csv_ok}")


if __name__ == "__main__":
    main()
