#!/usr/bin/env python3
"""exam_points 未整備の用語に、頻出の誤り肢・要点を一括付与する。"""
from __future__ import annotations

import csv
import importlib.util
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GLOSSARY_CSV = REPO / "data" / "glossary_terms.csv"

_spec = importlib.util.spec_from_file_location(
    "legacy", REPO / "tools" / "enrich_glossary_priority_legacy.py"
)
_legacy = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_legacy)

DEFAULT_EXAM_TIPS = _legacy.DEFAULT_EXAM_TIPS
patch_md = _legacy.patch_md
update_csv_row = _legacy.update_csv_row
sections_with_tips = _legacy.sections_with_tips

# slug → 試験で狙われる誤り肢（2〜3件）
EXTRA_TIPS: dict[str, list[str]] = {
    "airline-mask": [
        "「エアラインマスクは送気マスク」→ フィルター付きの密閉型",
        "「すべての粉じんに使用可」→ 対象物質・粒子径で選定",
    ],
    "anzen-eisei-kaizen-keikaku": [
        "「改善計画は任意の努力規定」→ 計画の策定・実施が義務",
        "「安全衛生委員会がなくても可」→ 体制とセットで出題",
    ],
    "anzen-eisei-kitei": [
        "「就業規則と同一」→ 事業場ごとの安全衛生規程",
        "「労安法本則に記載」→ 規程として整備",
    ],
    "anzen-eisei-kyoiku-kiroku": [
        "「教育記録の保存不要」→ 実施記録・保存期間あり",
        "「職長等教育は記録不要」→ 教育全般で記録",
    ],
    "anzen-iinkai": [
        "「安全衛生委員会と同一」→ 別組織・要件",
        "「50人未満でも必ず設置」→ 人数要件を確認",
    ],
    "benzene": [
        "「ベンゼンは急性毒性のみ」→ 発がん性・特別管理",
        "「許容濃度が高い」→ 管理濃度・特別管理物質",
    ],
    "bogo-tebukuro": [
        "「防護手袋で呼吸器も保護」→ 皮膚保護が目的",
        "「破れても交換不要」→ 浸透・破れで交換",
    ],
    "choryoku-hogo-gu": [
        "「耳栓と耳当ては効果同一」→ 騒音レベル・装着で選定",
        "「保護具不要区域があれば着用不要」→ 区域の定義",
    ],
    "choryoku-level": [
        "「聴力レベル＝騒音レベル」→ 聴力検査の結果指標",
        "「A特性のみで聴力評価」→ 健診所見と区別",
    ],
    "choukan-rodo-mensetu-shishin": [
        "「面接指導は衛生管理者が実施」→ 産業医（医師）",
        "「長時間労働者面接指導と同一」→ 別制度",
    ],
    "dai1shu-yuki-yozai": [
        "「第1種はすべて特別有機溶剤」→ 区分表で確認",
        "「第2種より規制が緩い」→ 第1種の方が厳しい場面",
    ],
    "dai2shu-yuki-yozai": [
        "「第2種は特別教育不要」→ 作業の態様で教育要件",
    ],
    "dai3shu-yuki-yozai": [
        "「第3種は健康診断不要」→ 区分により健診・措置あり",
    ],
    "dakt-atsuryoku-sonshitsu": [
        "「ダクト損失は換気量に無関係」→ 排風機選定に影響",
    ],
    "eisei-kanrisha-shokumu": [
        "「専任でなくても巡視不要」→ 専任・兼務で職務が異なる",
        "「衛生管理者＝産業医の職務」→ 役割分担",
    ],
    "eki-hoshu": [
        "「液捕集は粉じん採取」→ ガス・蒸気向け",
    ],
    "formaldehyde": [
        "「フォルマルデヒドは発がん性なし」→ 化学物質リスクで確認",
    ],
    "fushindo-hakkan": [
        "「発汗のみが熱放散」→ 不感蒸泄も重要",
    ],
    "gaitsuke-kyokuhai": [
        "「外付け型は制御風速不要」→ フード型と同様に風速",
    ],
    "ginou-koushu": [
        "「技能講習＝特別教育」→ 別制度・対象",
    ],
    "haifu-ki-seiatsu": [
        "「静圧と換気量は無関係」→ 特性曲線で選定",
    ],
    "haiki-ko": [
        "「排気口は給気口と同位置でよい」→ 気流・再循環に注意",
    ],
    "hakurou": [
        "「白ろう＝石綿」→ 別物質・規制",
    ],
    "hassan-kyodo-kanki-ryo": [
        "「希釈換気は局所排気の代わり」→ 発散強度・必要換気量",
    ],
    "hatsugansei": [
        "「発がん性＝急性毒性」→ 長期・確率的影響",
    ],
    "heni-gensei": [
        "「変異原性＝発がん性と同義」→ 別の有害性",
    ],
    "hibaku": [
        "「被ばくは医療のみ」→ 工業放射線でも管理",
    ],
    "hifu-kyushu": [
        "「吸入のみがばく露」→ 皮膚吸収経路あり",
    ],
    "hinan-keiro": [
        "「避難経路は努力規定」→ 安全衛生上の整備",
    ],
    "hogo-gu-fuyou-kuiki": [
        "「不要区域があれば全作業場で着用不要」→ 区域の限定",
    ],
    "hogo-gu-tekiousei-kensa": [
        "「適合性検査は呼吸用のみ」→ 保護具全般の場面",
    ],
    "hoshasen-gyomu": [
        "「放射線業務は医療のみ」→ 工業利用含む",
    ],
    "hoshu-kouritsu": [
        "「捕集効率100%が必須」→ 測定・評価の文脈",
    ],
    "hyoshiki-keiji": [
        "「標識掲示は任意」→ 法令・規則で義務の場面",
    ],
    "ishiwata-funjin": [
        "「石綿粉じん＝一般粉じん」→ 石綿障害防止規則",
    ],
    "jinpai-kanri-kubun": [
        "「管理区分は濃度のみ」→ 測定・健診・措置のセット",
    ],
    "judo-kitsuen-boshi": [
        "「受動喫煙防止は労安法にない」→ 関連規制・措置",
    ],
    "junka": [
        "「熱順化は発汗と同義」→ 体への熱移動の過程",
    ],
    "jyozu-kuuki-seijo": [
        "「除じん装置があれば局所排気不要」→ 補完関係",
    ],
    "jyunyu-sochi": [
        "「授乳中は就業禁止のみ」→ 措置・配慮",
    ],
    "kagaku-bougo-fuku": [
        "「化学防護服＝防護衣のみ」→ 全身防護・気密性",
    ],
    "kagaku-busshitsu-kiken-chosa": [
        "「SDSがあれば調査不要」→ 有害性調査等は別義務",
    ],
    "kakomi-kyokuho-haiki": [
        "「囲い型は外付けと同じ」→ 構造・制御風速",
    ],
    "kakuho-kanki": [
        "「確保換気は局所排気の代わり」→ 全体換気の補完",
    ],
    "kakuteiteki-kakuritsu-eikyo": [
        "「確定的影響は確率のみ」→ 閾値・確率の区別",
    ],
    "kan-i-sokutei-kiki": [
        "「簡易測定で管理区分決定」→ 正式測定の流れ",
    ],
    "kanri-kubun-dai1": [
        "「第1管理は測定不要」→ 厳しい管理・測定",
    ],
    "kanri-kubun-dai2": [
        "「第2管理は改善措置不要」→ 管理区分ごとの措置",
    ],
    "kanri-kubun-dai3": [
        "「第3管理は記録不要」→ 測定・記録あり",
    ],
    "kanri-zu": [
        "「管理図は作業環境測定のみ」→ 濃度推移の管理",
    ],
    "kansaku": [
        "「感作＝急性中毒」→ 過敏症・遅発",
    ],
    "kenmu-eisei-kanrisha": [
        "「兼務は選任不要」→ 専任と職務が異なる",
    ],
    "kojin-sampling-ho": [
        "「個人サンプリングは作業環境測定と同義」→ 個人ばく露",
    ],
    "kokukyuon-kankyuon-shitsukyu": [
        "「黒球温度＝気温のみ」→ WBGTの構成要素",
    ],
    "kokyuyo-hogo-gu-sentei": [
        "「送気マスクは選定不要」→ 作業内容・濃度で選定",
    ],
    "koukiatsu-sagyo": [
        "「高気圧作業は増圧のみ問題」→ 減圧症・減圧手順",
    ],
    "kyokuhai-seino-kensa": [
        "「性能検査は任意」→ 設置・変更時等",
    ],
    "menkyo-shinsei": [
        "「試験合格＝即免許」→ 申請・交付手続",
    ],
    "namari-sagyo": [
        "「鉛作業は一般化学物質と同じ」→ 鉛中毒予防規則",
    ],
    "necchiren": [
        "「熱けいれん＝熱射病」→ 別の熱中症",
    ],
    "nenshosha-shugyo-seigen": [
        "「年少者制限は努力規定」→ 就業制限・年齢",
    ],
    "ninsanpu-kenko-hoji": [
        "「妊産婦措置は健診のみ」→ 就業上の措置含む",
    ],
    "nintei-eisei-hyokashi": [
        "「認定衛生評価士＝作業環境測定士」→ 別資格",
    ],
    "nissabyo": [
        "「日射病＝熱射病」→ 別分類の熱中症",
    ],
    "raynaud": [
        "「レイノー現象は騒音障害」→ 振動・寒冷等",
    ],
    "seishoku-dokusei": [
        "「生殖毒性＝急性毒性」→ 別の有害性区分",
    ],
    "sekimen-shogai-yobo": [
        "「石綿規則と同一」→ 石綿以外の粉じんも対象の場面",
    ],
    "shinya-gyou": [
        "「深夜業は健診不要」→ 深夜業健診",
    ],
    "shogeki-on": [
        "「衝撃音＝連続騒音と同じ評価」→ 測定方法が異なる",
    ],
    "shokumu-tekisei-kensa": [
        "「職務適性検査＝健康診断」→ 別検査",
    ],
    "sochi-a": [
        "「措置Aは措置Bより緩い」→ 就業上の措置の段階",
    ],
    "sochi-b": [
        "「措置Bは就業禁止のみ」→ 配置転換等含む",
    ],
    "souki-masuk": [
        "「送気マスクはフィルター不要」→ 送気源・選定",
    ],
    "soun-shogai": [
        "「騒音障害は一時的聴力低下のみ」→ 難聴・NIHL",
    ],
    "tachiire-kinshi": [
        "「立入禁止は標識のみ」→ 管理区域・酸素欠乏等",
    ],
    "taion-chosetsu": [
        "「体温調節は発汗のみ」→ 血管拡張・順化",
    ],
    "te-saki-shindo": [
        "「手先振動は全身振動と同じ基準」→ 別規制",
    ],
    "tetraalkyl-lead": [
        "「有機鉛は無機鉛と同じ」→ 特別な管理・健診",
    ],
    "toka-hoshu": [
        "「等価騒音レベル＝瞬間値」→ 時間加重",
    ],
    "tokubetsu-kanri-busshitsu": [
        "「特別管理＝特定化学物質と同義」→ 別区分",
    ],
    "tokutei-kagaku-sagyo": [
        "「特定化学物質作業は鉛作業と同じ」→ 別規則",
    ],
    "trichloroethylene": [
        "「トリクロロエチレンは管理不要」→ 有機溶剤・管理濃度",
    ],
    "yuki-yozai-sagyo": [
        "「有機溶剤作業は区分不要」→ 第1〜3種・特別",
    ],
    "zenmenkaze": [
        "「全面排風は局所排気の代わり」→ 作業場全体の換気",
    ],
    "zenshin-shindo": [
        "「全身振動は手振動と同じ」→ 別基準・評価",
    ],
}


def keyword_tips(term: str, category: str) -> list[str]:
    tips: list[str] = []
    if "有機溶剤" in term or "溶剤" in term:
        tips.append("「有機溶剤の区分を混同」→ 物質名・作業態様で第1〜3種・特別を整理")
    if "管理区分" in term or "第" in term and "管理" in term:
        tips.append("「管理区分は濃度だけで決まる」→ 測定・評価・措置の流れ")
    if "保護具" in term or "防護" in term or "マスク" in term:
        tips.append("「保護具があれば作業環境改善不要」→ 両方が必要な場面")
    if "健診" in term or "健康診断" in term or "措置" in term:
        tips.append("「健診結果に就業上の措置は不要」→ 事後措置・健康管理")
    if "局所排気" in term or "換気" in term or "排気" in term:
        tips.append("「換気だけでばく露はゼロ」→ 発生源対策・局所排気")
    if category == "関係法令" and not tips:
        tips.append(f"「{term}は努力規定のみ」→ 義務・手続き・記録を法令条文で確認")
    if category == "労働生理" and not tips:
        tips.append(f"「{term}の症状を他疾患と混同」→ 原因・ばく露経路で区別")
    if not tips:
        short = term.split("・")[0][:12]
        tips.append(f"「{short}の定義・数値を類似語と混同」→ 本文の表と関連用語で比較")
        tips.append(f"「{short}は単独で完結する制度」→ 関連規則・手順とセットで復習")
    return tips[:3]


def tips_for_row(row: dict) -> list[str]:
    slug = row.get("slug", "")
    term = row.get("term", "")
    if term in DEFAULT_EXAM_TIPS:
        return list(DEFAULT_EXAM_TIPS[term])
    if slug in EXTRA_TIPS:
        return list(EXTRA_TIPS[slug])
    return keyword_tips(term, row.get("category", ""))


def main() -> None:
    with GLOSSARY_CSV.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    targets = [r for r in rows if not (r.get("exam_points") or "").strip()]
    md_ok = csv_ok = 0
    for row in targets:
        tips = tips_for_row(row)
        term = row["term"]
        slug = row["slug"]
        category = row.get("category", "労働衛生")
        raw_title = (row.get("title") or f"{term}とは？").split("【")[0].strip()
        if "とは" not in raw_title:
            raw_title = f"{term}とは？"
        csv_desc = (row.get("short_def") or row.get("definition") or "").strip()
        item = {
            "term": term,
            "slug": slug,
            "category": category,
            "title": raw_title,
            "csv_desc": csv_desc,
            "sections": [
                (
                    "定義の整理",
                    [
                        ["項目", "内容"],
                        ["用語", term],
                        ["要点", csv_desc or f"{term}の試験頻出ポイントを整理"],
                    ],
                ),
                ("試験で狙われる頻出ポイント", tips),
            ],
        }
        sections, merged_tips = sections_with_tips(item)
        if patch_md(item, sections):
            md_ok += 1
        if update_csv_row(term, slug, merged_tips, csv_desc):
            csv_ok += 1

    print(f"fill-remaining: targets={len(targets)}, md={md_ok}, csv={csv_ok}")


if __name__ == "__main__":
    main()
