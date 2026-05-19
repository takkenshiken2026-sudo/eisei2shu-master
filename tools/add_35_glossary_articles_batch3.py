#!/usr/bin/env python3
"""用語・詳細記事 第3弾35本追加（182〜216）。"""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTICLES = REPO / "eisei-articles" / "articles"
SLUG_JSON = REPO / "docs" / "glossary-article-slugs.json"
CHECKLIST_CSV = REPO / "docs" / "glossary-terms-checklist.csv"

_spec = importlib.util.spec_from_file_location(
    "batch1", REPO / "tools" / "add_35_glossary_articles.py"
)
_batch1 = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_batch1)
build_body = _batch1.build_body
build_frontmatter = _batch1.build_frontmatter


def T(
    order: int,
    file: str,
    term: str,
    slug: str,
    category: str,
    title: str,
    related: str,
    csv_desc: str,
    intent: str,
    sections: list | None = None,
) -> dict:
    if sections is None:
        sections = [
            (
                "試験での要点",
                [
                    ["観点", "確認すること"],
                    ["定義", f"{term}の意味と制度上の位置づけ"],
                    ["関連制度", "類似用語・規則名とセットで整理"],
                ],
            ),
        ]
    return {
        "order": order,
        "file": file,
        "term": term,
        "slug": slug,
        "category": category,
        "title": title,
        "related": related,
        "csv_desc": csv_desc,
        "intent": intent,
        "sections": sections,
    }


NEW_TERMS = [
    T(182, "182-kyuin-saishu", "吸引採取", "kyuin-saishu", "労働衛生",
       "吸引採取とは？気集・捕集分析法・流量校正",
       "hoshu-bunseki-ho:捕集分析法;ryuryo-kosei:流量計の校正;rokka-hoshu:ろ過捕集",
       "ポンプ等で空気を吸引し試料を採取する方法です。作業環境測定の基本手順です。",
       "吸引採取の流れと、流量校正の重要性を理解すること。"),
    T(183, "183-eki-hoshu", "液捕集", "eki-hoshu", "労働衛生",
       "液捕集とは？ミゼット・洗気・ガス状物質",
       "mizetto-inpinja:ミゼットインピンジャー;hoshu-bunseki-ho:捕集分析法;kyuin-saishu:吸引採取",
       "液体に有害物質を吸収させて捕集する方法です。ガス・蒸気の測定で用いられます。",
       "液捕集の原理と、捕集液選定の要点を整理すること。"),
    T(184, "184-grab-sampling", "グラブサンプリング", "grab-sampling", "労働衛生",
       "グラブサンプリングとは？瞬間試料・ばく露評価",
       "kyuin-saishu:吸引採取;passive-sampler:パッシブサンプラー;kojin-sampling-ho:個人サンプリング法",
       "短時間の試料を一括採取する方法です。濃度の瞬間値把握に用いられます。",
       "グラブサンプリングの位置づけと、個人サンプリングとの違いを理解すること。"),
    T(185, "185-bogo-i", "防護衣", "bogo-i", "労働衛生",
       "防護衣とは？化学防護服・皮膚保護・選定",
       "kagaku-bougo-fuku:化学防護服;kojin-hogo-gu:個人用保護具;hifu-kyushu:皮膚吸収",
       "皮膚へのばく露を防ぐ保護具です。化学物質の性状に応じた選定が重要です。",
       "防護衣の選定と、工程対策との優先順位を整理すること。"),
    T(186, "186-bogo-tebukuro", "防護手袋", "bogo-tebukuro", "労働衛生",
       "防護手袋とは？浸透・破れ・皮膚吸収対策",
       "bogo-i:防護衣;hifu-kyushu:皮膚吸収;kojin-hogo-gu:個人用保護具",
       "手の皮膚を守る保護具です。物質による浸透・貫通の違いが試験に出ます。",
       "防護手袋の選定と交換の考え方を理解すること。"),
    T(187, "187-hogo-megane", "保護メガネ", "hogo-megane", "労働衛生",
       "保護メガネとは？飛沫・粉じん・化学物質",
       "kojin-hogo-gu:個人用保護具;funzin-shogai-boshi:粉じん障害防止規則;ghs:GHS",
       "眼へのばく露を防ぐ保護具です。側板付きなど形状の違いが論点になります。",
       "保護メガネの種類と使用場面を整理すること。"),
    T(188, "188-airline-mask", "エアラインマスク", "airline-mask", "労働衛生",
       "エアラインマスクとは？送気マスク・ホース供給",
       "souki-masuk:送気マスク;boudoku-masuk:防毒マスク;hogo-gu-tekiousei-kensa:保護具着用適合性検査",
       "外部から清浄空気を送る呼吸用保護具の一種です。送気マスクとセットで整理します。",
       "エアラインマスクの特徴と、使用上の注意を理解すること。"),
    T(189, "189-kagaku-bougo-fuku", "化学防護服", "kagaku-bougo-fuku", "労働衛生",
       "化学防護服とは？液密・気密・選定レベル",
       "bogo-i:防護衣;tokutei-kagaku-busshitsu-shogai-yobo:特定化学物質障害予防規則;kojin-hogo-gu:個人用保護具",
       "高リスク化学物質作業で用いる防護服です。液密・気密などの区分が問われます。",
       "化学防護服の区分と、保護具不要区域との関係を整理すること。"),
    T(190, "190-hatsugansei", "発がん性", "hatsugansei", "労働生理",
       "発がん性とは？特別管理物質・ベンゼン",
       "benzene:ベンゼン;tokubetsu-kanri-busshitsu:特別管理物質;kagaku-busshitsu-dokusho:化学物質の急性毒性・慢性毒性",
       "長期ばく露でがんのリスクが高まる性質です。管理物質区分と関連します。",
       "発がん性の意味と、厳格な管理の理由を理解すること。"),
    T(191, "191-heni-gensei", "変異原性", "heni-gensei", "労働生理",
       "変異原性とは？遺伝毒性・化学物質管理",
       "hatsugansei:発がん性;ghs:GHS;risk-assessment:リスクアセスメント",
       "遺伝子への損傷のおそれがある性質です。GHS分類とリスク評価に関係します。",
       "変異原性の定義と、発がん性との整理をすること。"),
    T(192, "192-seishoku-dokusei", "生殖毒性", "seishoku-dokusei", "労働生理",
       "生殖毒性とは？妊娠・授乳・化学物質",
       "ninshin-sochi:妊娠中の措置;jyunyu-sochi:授乳中の措置;ninsanpu-kenko-hoji:妊産婦の健康保持",
       "生殖能や胎児への影響のおそれがある毒性です。妊産婦保護と接続します。",
       "生殖毒性の意味と、就業上の措置との関係を整理すること。"),
    T(193, "193-zenshin-shindo", "全身振動", "zenshin-shindo", "労働生理",
       "全身振動とは？運搬車両・振動障害",
       "te-saki-shindo:手先振動;shindo-shogai:振動障害;shindo-hyoka:振動の評価",
       "体全体に伝わる振動です。フォークリフト等の運転作業で問題になります。",
       "全身振動と手先振動の違いを整理すること。"),
    T(194, "194-te-saki-shindo", "手先振動", "te-saki-shindo", "労働生理",
       "手先振動とは？振動工具・白ろう・レイノー",
       "zenshin-shindo:全身振動;hakurou:白ろう;raynaud:レイノー現象",
       "振動工具などで手に伝わる振動です。振動障害の中心テーマです。",
       "手先振動のばく露評価と健康影響を理解すること。"),
    T(195, "195-hakurou", "白ろう", "hakurou", "労働生理",
       "白ろうとは？振動障害・手指の蒼白",
       "raynaud:レイノー現象;te-saki-shindo:手先振動;shindo-shogai:振動障害",
       "寒冷や振動で手指が蒼白になる症状です。振動障害の代表例です。",
       "白ろうの特徴と、レイノー現象との関係を整理すること。"),
    T(196, "196-raynaud", "レイノー現象", "raynaud", "労働生理",
       "レイノー現象とは？振動・寒冷・血流障害",
       "hakurou:白ろう;te-saki-shindo:手先振動;shindo-shogai-boshi-shishin:振動障害防止指針",
       "血管の痙攣により手指の色調が変わる現象です。振動ばく露と関連します。",
       "レイノー現象の原因と、振動障害予防の観点を理解すること。"),
    T(197, "197-shogeki-on", "衝撃音", "shogeki-on", "労働衛生",
       "衝撃音とは？騒音測定・評価量",
       "renzoku-souon:連続騒音;toka-sonn-level:等価騒音レベル;a-tokusei-soryo-on:A特性騒音レベル",
       "瞬間的に大きい騒音です。騒音測定の評価方法と関連します。",
       "衝撃音と連続騒音の違いを整理すること。"),
    T(198, "198-renzoku-souon", "連続騒音", "renzoku-souon", "労働衛生",
       "連続騒音とは？等価騒音レベル・作業環境",
       "shogeki-on:衝撃音;toka-sonn-level:等価騒音レベル;sagyo-kankyo-sokutei:作業環境測定",
       "比較的安定して続く騒音です。等価騒音レベルで評価されます。",
       "連続騒音の評価方法と、聴力保護具選定との関係を理解すること。"),
    T(199, "199-choryoku-level", "聴力レベル", "choryoku-level", "労働生理",
       "聴力レベルとは？聴力検査・騒音性難聴",
       "soonnsei-nacho:騒音性難聴;teiki-kenko-shindan:定期健康診断;choryoku-hogo-gu:聴力保護具",
       "健康診断の聴力検査で用いる指標です。騒音性難聴の判定に関係します。",
       "聴力レベルの意味と、配置転換の判断との接続を整理すること。"),
    T(200, "200-soun-shogai", "騒音障害", "soun-shogai", "労働生理",
       "騒音障害とは？騒音性難聴・予防対策",
       "soonnsei-nacho:騒音性難聴;choryoku-hogo-gu:聴力保護具;sagyo-kankyo-sokutei:作業環境測定",
       "騒音ばく露による健康障害の総称です。測定・保護具・健診がセットで出ます。",
       "騒音障害の予防の流れを整理すること。"),
    T(201, "201-ninshin-sochi", "妊娠中の措置", "ninshin-sochi", "関係法令",
       "妊娠中の措置とは？妊産婦保護・作業制限",
       "ninsanpu-kenko-hoji:妊産婦の健康保持;shugyo-jo-sochi:就業上の措置;seishoku-dokusei:生殖毒性",
       "妊娠中の労働者に対する就業上の配慮です。時間外・深夜業の制限などが論点です。",
       "妊娠中の措置の内容と、産前産後の措置との違いを整理すること。"),
    T(202, "202-jyunyu-sochi", "授乳中の措置", "jyunyu-sochi", "関係法令",
       "授乳中の措置とは？妊産婦・有害物質作業",
       "ninshin-sochi:妊娠中の措置;ninsanpu-kenko-hoji:妊産婦の健康保持;tokubetsu-kanri-busshitsu:特別管理物質",
       "授乳中の労働者に対する保護措置です。有害業務への就業制限と関連します。",
       "授乳中の措置の要点を、妊娠中の措置と比較して覚えること。"),
    T(203, "203-kyouryokusha", "協力者", "kyouryokusha", "関係法令",
       "協力者とは？酸素欠乏作業・立入・救助",
       "kanshi-nin:監視人;kyuujo-youi-sha:救助要預者;sanso-ketsubosho-yobo:酸素欠乏症等防止規則",
       "危険作業で作業者を支援する者です。監視人・救助体制とセットで問われます。",
       "協力者の役割と、監視人との違いを整理すること。"),
    T(204, "204-sanso-noudo-kei", "酸素濃度計", "sanso-noudo-kei", "労働衛生",
       "酸素濃度計とは？酸素欠乏・測定・校正",
       "sanso-ketsubosho-sokutei:酸素濃度測定;kenchi-kan:検知管;kan-i-sokutei-kiki:簡易測定機器",
       "空気中の酸素濃度を測る器具です。作業開始前測定の必須機器です。",
       "酸素濃度計の使用場面と、測定タイミングを理解すること。"),
    T(205, "205-kan-i-sokutei-kiki", "簡易測定機器", "kan-i-sokutei-kiki", "労働衛生",
       "簡易測定機器とは？検知管・直接読み取り",
       "kenchi-kan:検知管;chokusetsu-yomitori-sokutei:直接読み取り式測定;sagyo-kankyo-sokutei:作業環境測定",
       "手軽に濃度を把握する測定器です。正式な作業環境測定との使い分けが重要です。",
       "簡易測定機器の利点と限界を整理すること。"),
    T(206, "206-kanri-kubun-dai1", "第1管理", "kanri-kubun-dai1", "労働衛生",
       "第1管理（作業環境管理区分）とは？措置・再測定",
       "sagyo-kankyo-kanri-kubun:作業環境管理区分;sochi-a:措置A;kanri-nodo:管理濃度",
       "作業環境管理区分の一つです。管理濃度超過時の措置が問われます。",
       "第1管理の意味と、第2・第3管理との違いを表で整理すること。"),
    T(207, "207-kanri-kubun-dai2", "第2管理", "kanri-kubun-dai2", "労働衛生",
       "第2管理（作業環境管理区分）とは？改善・再評価",
       "kanri-kubun-dai1:第1管理;kanri-kubun-dai3:第3管理;sagyo-kankyo-hyoka:作業環境評価",
       "中間的な管理区分です。測定結果と許容・管理濃度の関係で判定します。",
       "第2管理の位置づけと、必要な措置を理解すること。"),
    T(208, "208-kanri-kubun-dai3", "第3管理", "kanri-kubun-dai3", "労働衛生",
       "第3管理（作業環境管理区分）とは？良好な作業環境",
       "kanri-kubun-dai1:第1管理;kanri-kubun-dai2:第2管理;kyoyo-nodo:許容濃度",
       "比較的良好な作業環境の区分です。管理区分の判定フローで押さえます。",
       "第3管理の条件と、再測定・表示義務との関係を整理すること。"),
    T(209, "209-sochi-a", "措置A", "sochi-a", "労働衛生",
       "措置Aとは？作業環境管理・改善工事",
       "sochi-b:措置B;kanri-kubun-dai1:第1管理;sagyo-kankyo-hyoka:作業環境評価",
       "管理区分に応じて講じる改善措置の一つです。措置Bとの違いが頻出です。",
       "措置Aの内容と、実施期限・再評価との流れを理解すること。"),
    T(210, "210-sochi-b", "措置B", "sochi-b", "労働衛生",
       "措置Bとは？作業環境管理・工程改善",
       "sochi-a:措置A;sagyo-kankyo-kanri-kubun:作業環境管理区分;risk-assessment:リスクアセスメント",
       "作業環境を改善するための措置です。措置Aとあわせて暗記表にすると覚えやすいです。",
       "措置Bの要点と、局所排気・換気との関係を整理すること。"),
    T(211, "211-ginou-koushu", "技能講習", "ginou-koushu", "関係法令",
       "技能講習とは？作業主任者・免許・資格",
       "sagyoshunin-sha:作業主任者;yuki-yozai-sagyo-shunin:有機溶剤作業主任者;menkyo-shinsei:免許申請",
       "危険有害作業で必要となる技能の習得講習です。作業主任者選任の要件と関連します。",
       "技能講習と特別教育・安全衛生教育の違いを整理すること。"),
    T(212, "212-sennin-eisei-kanrisha", "専任の衛生管理者", "sennin-eisei-kanrisha", "関係法令",
       "専任の衛生管理者とは？選任要件・兼務の禁止",
       "kenmu-eisei-kanrisha:兼務の衛生管理者;eisei-kanrisha-shokumu:衛生管理者の職務;eisei-kanrisha:衛生管理者",
       "衛生管理業務に専念する衛生管理者です。事業場規模により専任が必要になります。",
       "専任の要件と、兼務が認められる条件を表で整理すること。"),
    T(213, "213-kenmu-eisei-kanrisha", "兼務の衛生管理者", "kenmu-eisei-kanrisha", "関係法令",
       "兼務の衛生管理者とは？専任義務・労働時間",
       "sennin-eisei-kanrisha:専任の衛生管理者;eisei-kanrisha:衛生管理者;anzen-kanrisha:安全管理者",
       "他業務と兼ねる衛生管理者です。専任が必要な規模では選任できません。",
       "兼務の可否と、試験での誤り選択肢を整理すること。"),
    T(214, "214-nintei-eisei-hyokashi", "認定衛生評価士", "nintei-eisei-hyokashi", "労働衛生",
       "認定衛生評価士とは？作業環境評価・測定",
       "sagyo-kankyo-sokutei-shi:作業環境測定士;sagyo-kankyo-hyoka:作業環境評価;nintei-kikan:認定機関",
       "作業環境の評価等を行う国家資格者です。測定士・認定機関と役割分担します。",
       "認定衛生評価士の職務範囲を、測定士と区別して覚えること。"),
    T(215, "215-hinan-keiro", "避難経路", "hinan-keiro", "労働衛生",
       "避難経路とは？酸素欠乏・緊急時対策",
       "hinan-kigu:避難器具;sanso-ketsubosho-yobo:酸素欠乏症等防止規則;anzen-eisei-kaizen-keikaku:安全衛生改善計画",
       "緊急時に安全に退避するための経路です。危険作業場の安全管理と関連します。",
       "避難経路の確保と、避難器具・救助体制との関係を理解すること。"),
    T(216, "216-kyuujo-youi-sha", "救助要預者", "kyuujo-youi-sha", "関係法令",
       "救助要預者とは？酸素欠乏作業・緊急連絡",
       "kanshi-nin:監視人;kyouryokusha:協力者;hinan-keiro:避難経路",
       "危険作業で救助体制を担う者です。監視人・協力者とセットで手順を覚えます。",
       "救助要預者の役割と、作業開始前の準備を整理すること。"),
]


def main() -> None:
    slug_map: dict[str, str] = json.loads(SLUG_JSON.read_text(encoding="utf-8"))
    existing_slugs = set(slug_map.values())
    created = 0
    for item in NEW_TERMS:
        if item["slug"] in existing_slugs or item["term"] in slug_map:
            print(f"skip: {item['term']} ({item['slug']})")
            continue
        md_path = ARTICLES / f"{item['file']}.md"
        fm = build_frontmatter(item).replace(
            "用語35本追加バッチ", "用語35本追加バッチ（第3弾）"
        )
        body = build_body(item["term"], item["title"], item["category"], item["sections"])
        md_path.write_text(fm + "\n\n" + body, encoding="utf-8")
        slug_map[item["term"]] = item["slug"]
        existing_slugs.add(item["slug"])
        created += 1
        print(f"created: {md_path.name}")

    SLUG_JSON.write_text(
        json.dumps(slug_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    with CHECKLIST_CSV.open(encoding="utf-8", newline="") as f:
        all_rows = list(csv.reader(f))
    existing_terms = {r[1] for r in all_rows[1:] if len(r) > 1}
    with CHECKLIST_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in all_rows:
            writer.writerow(row)
        for item in NEW_TERMS:
            if item["term"] not in existing_terms:
                writer.writerow([item["category"], item["term"], item["csv_desc"]])
                existing_terms.add(item["term"])

    print(f"done: {created} articles, {len(set(slug_map.values()))} unique slugs")


if __name__ == "__main__":
    main()
