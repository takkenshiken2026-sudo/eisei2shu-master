#!/usr/bin/env python3
"""用語・詳細記事 第2弾35本追加（147〜181）。"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
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
DATE = _batch1.DATE


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
    T(
        147,
        "147-rokka-hoshu",
        "ろ過捕集",
        "rokka-hoshu",
        "労働衛生",
        "ろ過捕集とは？固体捕集・フィルター採取の要点",
        "hoshu-bunseki-ho:捕集分析法;kishuu:気集;chokusetsu-yomitori-sokutei:直接読み取り式測定",
        "粒子状物質をフィルター等に捕集する方法です。捕集分析法・気集とセットで試験に出ます。",
        "ろ過捕集の仕組みと、流量・捕集材選定の重要性を理解すること。",
        [
            (
                "ろ過捕集の基本",
                [
                    ["項目", "内容"],
                    ["対象", "粉じんなどの粒子状物質"],
                    ["注意点", "流量校正・適切なフィルター選定"],
                ],
            ),
        ],
    ),
    T(
        148,
        "148-chikan-kanki",
        "置換換気",
        "chikan-kanki",
        "労働衛生",
        "置換換気とは？全面換気・確保換気との違い",
        "zenmenkaze:全面換気・希釈換気;kakuho-kanki:確保換気;kyokuho-haikisochi:局所排気装置",
        "室内空気をきれいな外気で置き換える換気方式です。希釈換気・確保換気との違いが問われます。",
        "置換換気の目的と、局所排気優先の原則を整理すること。",
    ),
    T(
        149,
        "149-sagyo-kankyo-sokutei-kiroku",
        "作業環境測定記録",
        "sagyo-kankyo-sokutei-kiroku",
        "労働衛生",
        "作業環境測定記録とは？保存期間・掲示・管理簿",
        "sagyo-kankyo-sokutei:作業環境測定;sagyo-kankyo-kanri-bo:作業環境管理簿;nintei-kikan:認定機関",
        "測定結果を記録し、労働者へ周知するための記録です。保存期間と管理簿との関係が頻出です。",
        "作業環境測定記録の保存・掲示要件を覚えること。",
        [
            (
                "記録の整理",
                [
                    ["記録", "保存の目安（学習用）"],
                    ["作業環境測定記録", "原則3年（代表例）"],
                    ["管理簿", "測定結果・管理区分などを記載"],
                ],
            ),
        ],
    ),
    T(
        150,
        "150-yuki-yozai-sagyo-shunin",
        "有機溶剤作業主任者",
        "yuki-yozai-sagyo-shunin",
        "関係法令",
        "有機溶剤作業主任者とは？選任要件・職務",
        "sagyoshunin-sha:作業主任者;yuki-yozai-chudoku-yobo-kisoku:有機溶剤中毒予防規則;yuki-yozai-kubun:有機溶剤の区分",
        "有機溶剤作業を安全に行うため選任する作業主任者です。技能講習・選任作業とセットで問われます。",
        "有機溶剤作業主任者の選任要件と職務を整理すること。",
    ),
    T(
        151,
        "151-tokutei-kagaku-sagyo-shunin",
        "特定化学物質作業主任者",
        "tokutei-kagaku-sagyo-shunin",
        "関係法令",
        "特定化学物質作業主任者とは？選任・職務の整理",
        "sagyoshunin-sha:作業主任者;tokutei-kagaku-busshitsu-shogai-yobo:特定化学物質障害予防規則;tokutei-kagaku-sagyo:特定化学物質作業",
        "特定化学物質作業の現場を統括する作業主任者です。規則ごとの作業主任者と混同しないよう整理します。",
        "特定化学物質作業主任者の位置づけを、他の作業主任者と区別して覚えること。",
    ),
    T(
        152,
        "152-namari-sagyo-shunin",
        "鉛作業主任者",
        "namari-sagyo-shunin",
        "関係法令",
        "鉛作業主任者とは？選任要件・鉛作業との関係",
        "namari-chudoku-yobo:鉛中毒予防規則;namari-sagyo:鉛作業;sagyoshunin-sha:作業主任者",
        "鉛作業を行う事業場で選任する作業主任者です。鉛中毒予防規則とセットで復習します。",
        "鉛作業主任者の選任と職務の要点を整理すること。",
    ),
    T(
        153,
        "153-sanso-kiken-sagyo-shunin",
        "酸素欠乏危険作業主任者",
        "sanso-kiken-sagyo-shunin",
        "関係法令",
        "酸素欠乏危険作業主任者とは？測定・立入管理",
        "sanso-ketsubosho-yobo:酸素欠乏症等防止規則;kanshi-nin:監視人;sanso-ketsubosho-sokutei:酸素濃度測定",
        "酸素欠乏等の危険作業を統括する作業主任者です。測定の実施と手順の順序が重要です。",
        "酸素欠乏危険作業主任者の役割と測定・監視人との関係を理解すること。",
    ),
    T(
        154,
        "154-netshabyo",
        "熱射病",
        "netshabyo",
        "労働生理",
        "熱射病とは？熱中症との違い・応急処置",
        "necchuysho:熱中症;wbgt:WBGT;taion-chosetsu:体温調節",
        "暑熱環境で体温調節が破綻し、生命に関わる重症の熱疾患です。熱中症の段階整理で押さえます。",
        "熱射病の重症度と、熱中症・日射病との違いを整理すること。",
        [
            (
                "熱中症の段階（整理）",
                [
                    ["段階", "特徴"],
                    ["軽症", "めまい・脱力など"],
                    ["熱射病", "意識障害・体温上昇など重篤"],
                ],
            ),
        ],
    ),
    T(
        155,
        "155-necchiren",
        "熱けいれん",
        "necchiren",
        "労働生理",
        "熱けいれんとは？暑熱環境での筋肉痙攣",
        "necchuysho:熱中症;wbgt:WBGT;fushindo-hakkan:不感蒸泄・発汗",
        "大量の発汗で塩分が失われ、筋肉がけいれんする熱中症の一種です。",
        "熱けいれんの原因と対策（水分・塩分補給）を理解すること。",
    ),
    T(
        156,
        "156-nissabyo",
        "日射病",
        "nissabyo",
        "労働生理",
        "日射病とは？直射日光・熱中症との関係",
        "necchuysho:熱中症;netshabyo:熱射病;wbgt:WBGT",
        "直射日光などによる熱中症です。WBGTや作業・休憩管理と関連して問われます。",
        "日射病の発生要因と、現場での予防策を整理すること。",
    ),
    T(
        157,
        "157-shinri-fuka",
        "心理的負荷",
        "shinri-fuka",
        "関係法令",
        "心理的負荷とは？ストレスチェック・長時間労働",
        "stress-check:ストレスチェック;choujikan-rodo-mensetu:長時間労働者面接指導;sangyo-i:産業医",
        "仕事の精神的負担を評価する概念です。ストレスチェック制度と関連して出題されます。",
        "心理的負荷の意味と、ストレスチェック・面接指導との関係を整理すること。",
    ),
    T(
        158,
        "158-jigyosha-ippan-gimu",
        "事業者の一般義務",
        "jigyosha-ippan-gimu",
        "関係法令",
        "事業者の一般義務とは？労働安全衛生法の総義務",
        "rodo-anzen-eisei-ho:労働安全衛生法;anzen-eisei-kanri-taisei:安全衛生管理体制;risk-assessment:リスクアセスメント",
        "事業者が負う安全衛生上の基本義務です。法の根拠として頻出の論点になります。",
        "事業者の一般義務の内容と、個別規則の義務との関係を理解すること。",
    ),
    T(
        159,
        "159-anzen-eisei-kitei",
        "安全衛生規程",
        "anzen-eisei-kitei",
        "関係法令",
        "安全衛生規程とは？作成・周知・記録",
        "rodo-anzen-eisei-kisoku:労働安全衛生規則;anzen-eisei-kyoiku:安全衛生教育;eisei-kanrisha:衛生管理者",
        "事業場の安全衛生上のルールを定めた規程です。作成義務と周知が問われます。",
        "安全衛生規程の目的と、教育・管理体制との関係を整理すること。",
    ),
    T(
        160,
        "160-kenchi-kan",
        "検知管",
        "kenchi-kan",
        "労働衛生",
        "検知管とは？直接読み取り式測定・簡易測定",
        "chokusetsu-yomitori-sokutei:直接読み取り式測定;sagyo-kankyo-sokutei:作業環境測定;hoshu-bunseki-ho:捕集分析法",
        "ガス濃度を簡易に測る直接読み取り式の器具です。捕集分析法との使い分けが出ます。",
        "検知管の特徴と、正式な作業環境測定との違いを整理すること。",
    ),
    T(
        161,
        "161-passive-sampler",
        "パッシブサンプラー",
        "passive-sampler",
        "労働衛生",
        "パッシブサンプラーとは？拡散採取・個人ばく露",
        "kojin-sampling-ho:個人サンプリング法;hoshu-bunseki-ho:捕集分析法;kojin-hogo-gu:個人用保護具",
        "拡散により試料を採取する方法・器具です。個人サンプリングと関連します。",
        "パッシブサンプラーの原理と、吸引採取との違いを理解すること。",
    ),
    T(
        162,
        "162-hoshu-kouritsu",
        "捕集効率",
        "hoshu-kouritsu",
        "労働衛生",
        "捕集効率とは？局所排気・ろ過捕集の性能",
        "kyokuhai-seino-kensa:局所排気装置の性能検査;rokka-hoshu:ろ過捕集;fudo-kyokuhai:フード型局所排気装置",
        "有害物質をどれだけ捕集できたかを示す指標です。局所排気の性能評価に関係します。",
        "捕集効率の意味と、性能検査・フード設計との関係を整理すること。",
    ),
    T(
        163,
        "163-kyokuhai-seino-kensa",
        "局所排気装置の性能検査",
        "kyokuhai-seino-kensa",
        "労働衛生",
        "局所排気装置の性能検査とは？実施時期・方法",
        "kyokuho-haikisochi:局所排気装置;haifu-ki-seiatsu:排風機の静圧;hoshu-kouritsu:捕集効率",
        "局所排気装置が設計どおり機能するか確認する検査です。",
        "性能検査の目的と、ダクト・排風機・フードとの関係を理解すること。",
    ),
    T(
        164,
        "164-kyuki-ko",
        "給気口",
        "kyuki-ko",
        "労働衛生",
        "給気口とは？換気の気流・全面換気の設計",
        "haiki-ko:排気口;kiryu-haifu:気流分布;zenmenkaze:全面換気・希釈換気",
        "きれいな空気を室内に送り込む開口です。排気口との位置関係が換気効率に影響します。",
        "給気口と排気口の役割、気流分布との関係を整理すること。",
    ),
    T(
        165,
        "165-haiki-ko",
        "排気口",
        "haiki-ko",
        "労働衛生",
        "排気口とは？局所排気・全面換気での位置",
        "kyuki-ko:給気口;kyokuho-haikisochi:局所排気装置;kiryu-haifu:気流分布",
        "汚染空気を屋外へ排出する開口です。発散源との位置関係が重要です。",
        "排気口の設置上の要点と、給気とのバランスを理解すること。",
    ),
    T(
        166,
        "166-jikko-senryo",
        "実効線量",
        "jikko-senryo",
        "労働生理",
        "実効線量とは？線量限度・被ばく管理",
        "hibaku:被ばく;denri-hoshasen:電離放射線;kakuteiteki-kakuritsu-eikyo:確定的影響と確率的影響",
        "防護のための線量指標の一つです。被ばく限度の管理に用いられます。",
        "実効線量の意味と、確定的・確率的影響との整理をすること。",
    ),
    T(
        167,
        "167-hibaku",
        "被ばく",
        "hibaku",
        "労働生理",
        "被ばくとは？電離放射線・線量管理の基本",
        "jikko-senryo:実効線量;denri-hoshasen-shogai-yobo:電離放射線障害防止規則;alara:ALARA",
        "放射線や有害因子の影響を受けることです。電離放射線では線量管理が中心になります。",
        "被ばくの概念と、管理区域・線量限度との関係を整理すること。",
    ),
    T(
        168,
        "168-hoshasen-gyomu",
        "放射線業務",
        "hoshasen-gyomu",
        "関係法令",
        "放射線業務とは？管理区域・記録・教育",
        "denri-hoshasen-shogai-yobo:電離放射線障害防止規則;kanri-kuiki-nyujo:管理区域への立入;kanri-zu:管理図",
        "電離放射線を使用する業務全般です。管理区域の設定や記録保存が問われます。",
        "放射線業務の管理の枠組みを、電離放射線規則とセットで覚えること。",
    ),
    T(
        169,
        "169-kanri-zu",
        "管理図",
        "kanri-zu",
        "労働衛生",
        "管理図とは？放射線業務・管理区域の表示",
        "kanri-kuiki-nyujo:管理区域への立入;hoshasen-gyomu:放射線業務;denri-hoshasen:電離放射線",
        "管理区域などを示す図面です。立入管理・表示義務と関連します。",
        "管理図の目的と、管理区域・標識との関係を理解すること。",
    ),
    T(
        170,
        "170-ishiwata-funjin",
        "石綿粉じん",
        "ishiwata-funjin",
        "労働生理",
        "石綿粉じんとは？ばく露・健康影響・予防",
        "ishiwata-sagyo:石綿作業;sekimen-shogai-yobo:石綿障害予防規則;jinpai:じん肺",
        "石綿による粉じんばく露です。石綿障害予防規則とじん肺の話題と接続します。",
        "石綿粉じんの健康リスクと、作業環境管理の考え方を整理すること。",
    ),
    T(
        171,
        "171-yugai-gyomu",
        "有害業務",
        "yugai-gyomu",
        "関係法令",
        "有害業務とは？第一種衛生管理者・試験範囲",
        "dai1shu-eisei-kanrisha:第一種衛生管理者;dai2shu-eisei-kanrisha:第二種衛生管理者;eisei-kanrisha:衛生管理者",
        "衛生管理者の区分や試験範囲を決めるうえで重要な概念です。",
        "有害業務の意味と、第一種・第二種衛生管理者の関係を整理すること。",
        [
            (
                "試験での見方",
                [
                    "第二種試験では有害業務に係る部分が除外される",
                    "第一種が必要な業種・有害業務の有無は引き続き頻出",
                ],
            ),
        ],
    ),
    T(
        172,
        "172-menkyo-shinsei",
        "免許申請",
        "menkyo-shinsei",
        "関係法令",
        "免許申請とは？衛生管理者・試験合格後の手続き",
        "eisei-kanrisha:衛生管理者;dai2shu-eisei-kanrisha:第二種衛生管理者;dai1shu-eisei-kanrisha:第一種衛生管理者",
        "試験合格後に行う免許の申請手続きです。申請期限などは公式要項で確認します。",
        "免許申請の流れを、選任要件とは別に整理すること。",
    ),
    T(
        173,
        "173-dai3shu-yuki-yozai",
        "第3種有機溶剤",
        "dai3shu-yuki-yozai",
        "関係法令",
        "第3種有機溶剤とは？区分と義務の違い",
        "dai1shu-yuki-yozai:第1種有機溶剤;dai2shu-yuki-yozai:第2種有機溶剤;yuki-yozai-kubun:有機溶剤の区分",
        "有機溶剤区分の一つです。特別・第1種・第2種とあわせて義務の差を表で整理します。",
        "第3種有機溶剤の位置づけと、他区分との比較をすること。",
    ),
    T(
        174,
        "174-yuki-yozai-sagyo",
        "有機溶剤作業",
        "yuki-yozai-sagyo",
        "関係法令",
        "有機溶剤作業とは？規則の対象・作業主任者",
        "yuki-yozai-chudoku-yobo-kisoku:有機溶剤中毒予防規則;yuki-yozai-sagyo-shunin:有機溶剤作業主任者;yuki-yozai-kubun:有機溶剤の区分",
        "有機溶剤を使用する作業全般を指します。規則の適用範囲の入口になります。",
        "有機溶剤作業の定義と、区分・作業環境管理の流れを整理すること。",
    ),
    T(
        175,
        "175-tokutei-kagaku-sagyo",
        "特定化学物質作業",
        "tokutei-kagaku-sagyo",
        "関係法令",
        "特定化学物質作業とは？規則・管理区分",
        "tokutei-kagaku-busshitsu-shogai-yobo:特定化学物質障害予防規則;tokutei-kagaku-sagyo-shunin:特定化学物質作業主任者;tokutei-kanri-busshitsu:特定管理物質",
        "特定化学物質を取り扱う作業です。物質ごとの管理区分が試験の中心です。",
        "特定化学物質作業の管理の型を、有機溶剤作業と比較して覚えること。",
    ),
    T(
        176,
        "176-namari-sagyo",
        "鉛作業",
        "namari-sagyo",
        "関係法令",
        "鉛作業とは？鉛中毒予防規則・作業環境管理",
        "namari-chudoku-yobo:鉛中毒予防規則;namari-sagyo-shunin:鉛作業主任者;kyoyo-nodo:許容濃度",
        "鉛や鉛化合物を取り扱う作業です。空気中濃度・健診・保護具がセットで出ます。",
        "鉛作業の対象範囲と、測定・健康診断の要点を整理すること。",
    ),
    T(
        177,
        "177-tetraalkyl-lead",
        "四アルキル鉛",
        "tetraalkyl-lead",
        "労働生理",
        "四アルキル鉛とは？鉛作業・皮膚吸収の注意",
        "namari-sagyo:鉛作業;hifu-kyushu:皮膚吸収;namari-chudoku-yobo:鉛中毒予防規則",
        "有機鉛化合物の代表例です。皮膚吸収などばく露経路の整理が重要です。",
        "四アルキル鉛の特性と、鉛作業規則上の扱いを理解すること。",
    ),
    T(
        178,
        "178-kuromusan",
        "クロム酸",
        "kuromusan",
        "労働生理",
        "クロム酸とは？特定化学物質・皮膚・呼吸器障害",
        "tokutei-kagaku-busshitsu-shogai-yobo:特定化学物質障害予防規則;kagaku-busshitsu-dokusho:化学物質の急性毒性・慢性毒性",
        "皮膚潰瘍や呼吸器障害のおそれがある物質の例です。特定化学物質の学習例として出ます。",
        "クロム酸の健康影響と、管理区分の考え方を整理すること。",
    ),
    T(
        179,
        "179-benzene",
        "ベンゼン",
        "benzene",
        "労働生理",
        "ベンゼンとは？特定化学物質・造血器への影響",
        "tokutei-kagaku-busshitsu-shogai-yobo:特定化学物質障害予防規則;tokubetsu-kanri-busshitsu:特別管理物質;kansaku:感作",
        "発がん性などが知られる芳香族炭化水素です。特別管理物質の代表例として整理します。",
        "ベンゼンの健康影響と、厳格な管理の理由を理解すること。",
    ),
    T(
        180,
        "180-trichloroethylene",
        "トリクロロエチレン",
        "trichloroethylene",
        "労働生理",
        "トリクロロエチレンとは？有機溶剤・中枢神経系",
        "yuki-yozai-kubun:有機溶剤の区分;yuki-yozai-chushinkei:有機溶剤による中枢神経系障害;kojin-hogo-gu:個人用保護具",
        "脱脂・洗浄などに用いられる有機溶剤です。中枢神経系への影響が試験で問われます。",
        "トリクロロエチレンのばく露経路と対策を整理すること。",
    ),
    T(
        181,
        "181-formaldehyde",
        "フォルマルデヒド",
        "formaldehyde",
        "労働生理",
        "フォルマルデヒドとは？刺激・感作・管理物質",
        "tokutei-kanri-busshitsu:特定管理物質;kansaku:感作;ghs:GHS",
        "刺激作用や感作性が知られる化学物質です。管理物質区分とGHS表示と関連します。",
        "フォルマルデヒドの健康影響と、リスク管理の要点を整理すること。",
    ),
]


def main() -> None:
    slug_map: dict[str, str] = json.loads(SLUG_JSON.read_text(encoding="utf-8"))
    existing_slugs = set(slug_map.values())
    created = 0
    for item in NEW_TERMS:
        if item["slug"] in existing_slugs:
            print(f"skip (exists): {item['slug']}")
            continue
        if item["term"] in slug_map:
            print(f"skip (term exists): {item['term']}")
            continue
        md_path = ARTICLES / f"{item['file']}.md"
        fm = build_frontmatter(item).replace(
            "用語35本追加バッチ", "用語35本追加バッチ（第2弾）"
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
        reader = csv.reader(f)
        all_rows = list(reader)
    existing_terms = {r[1] for r in all_rows[1:] if len(r) > 1}
    with CHECKLIST_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in all_rows:
            writer.writerow(row)
        for item in NEW_TERMS:
            term, desc, cat = item["term"], item["csv_desc"], item["category"]
            if term not in existing_terms:
                writer.writerow([cat, term, desc])
                existing_terms.add(term)

    print(f"done: {created} articles, {len(set(slug_map.values()))} unique slugs")


if __name__ == "__main__":
    main()
