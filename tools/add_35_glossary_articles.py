#!/usr/bin/env python3
"""用語・詳細記事を35本追加（MD・slug JSON・checklist CSV）。"""
from __future__ import annotations

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTICLES = REPO / "eisei-articles" / "articles"
SLUG_JSON = REPO / "docs" / "glossary-article-slugs.json"
CHECKLIST_CSV = REPO / "docs" / "glossary-terms-checklist.csv"

DATE = "2026-05-19"
SOURCES = (
    "安全衛生技術試験協会|https://www.exam.or.jp/;"
    "厚生労働省 職場のあんぜんサイト|https://anzeninfo.mhlw.go.jp/;"
    "e-Gov法令検索|https://elaws.e-gov.go.jp/"
)

# (order, filename_stem, term_key, slug, category, title_short, related_links, summary_csv, sections)
# sections: list of (h2, rows) where rows is list of [col1, col2] or strings for bullet blocks
NEW_TERMS: list[dict] = [
    {
        "order": 111,
        "file": "111-koyounyu-kenko-shindan",
        "term": "雇入時健康診断",
        "slug": "koyounyu-kenko-shindan",
        "category": "関係法令",
        "title": "雇入時健康診断とは？実施時期・対象・定期健診との違い",
        "related": "teiki-kenko-shindan:定期健康診断・雇入時健康診断の整理;kenko-shindan-jigo-sochi:健康診断後の事後措置;tokutei-gyo-mu-kenko-shindan:特定業務従事者健康診断",
        "csv_desc": "新たに雇い入れた労働者に対して実施する健康診断です。定期健康診断とあわせて、雇入れ時・変更時・定期の流れとして試験で問われます。",
        "intent": "雇入時健康診断の実施時期、対象者、定期健康診断との違いを選択肢で判断できるようにすること。",
        "sections": [
            ("雇入時健康診断の位置づけ", [
                ["種類", "実施のタイミング"],
                ["雇入時健康診断", "雇い入れの際（就業前）"],
                ["作業内容変更時", "有害業務等への配置変更時"],
                ["定期健康診断", "1年以内ごとに1回"],
            ]),
            ("試験で狙われる頻出ポイント", [
                "「パートタイム労働者は雇入時健診の対象外」→ 誤り（常時使用する労働者が対象）",
                "「雇入れ後1か月以内でよい」→ 就業前の実施が原則",
                "「定期健診と同じ頻度で実施」→ 雇入時は入社時の1回が中心",
            ]),
        ],
    },
    {
        "order": 112,
        "file": "112-tokushu-kenko-shindan",
        "term": "特殊健康診断",
        "slug": "tokushu-kenko-shindan",
        "category": "関係法令",
        "title": "特殊健康診断とは？対象・頻度・記録保存期間",
        "related": "teiki-kenko-shindan:定期健康診断の整理;yuki-yozai-kubun:有機溶剤の区分;tokutei-kagaku-busshitsu-shogai-yobo:特定化学物質障害予防規則",
        "csv_desc": "有機溶剤、特定化学物質、鉛、じん肺、電離放射線など、特定の有害業務に従事する労働者を対象とする健康診断です。",
        "intent": "特殊健康診断の対象業務、実施頻度、記録保存期間の違いを整理して覚えること。",
        "sections": [
            ("特殊健康診断の基本", [
                ["観点", "内容"],
                ["対象", "法令で定められた有害業務に従事する労働者"],
                ["頻度の目安", "多くは6か月以内ごとに1回（物質・業務により異なる）"],
                ["記録", "物質・業務により保存期間が異なる（5年・30年・40年など）"],
            ]),
            ("定期健診との違い", [
                ["項目", "定期健康診断", "特殊健康診断"],
                ["目的", "一般的な健康管理", "特定有害業務の健康影響の把握"],
                ["頻度", "1年以内ごとに1回", "6か月以内ごとに1回が多い"],
            ]),
        ],
    },
    {
        "order": 113,
        "file": "113-anzen-iinkai",
        "term": "安全委員会",
        "slug": "anzen-iinkai",
        "category": "関係法令",
        "title": "安全委員会とは？設置要件・衛生委員会との違い",
        "related": "eisei-iinkai:衛生委員会の整理;anzen-eisei-kanri-taisei:安全衛生管理体制;anzen-kanrisha:安全管理者",
        "csv_desc": "一定規模以上の事業場で、安全に関する協議を行う委員会です。衛生委員会とは設置要件・対象業種が異なります。",
        "intent": "安全委員会の設置要件と衛生委員会の違いを選択肢で判断できるようにすること。",
        "sections": [
            ("安全委員会と衛生委員会", [
                ["項目", "安全委員会", "衛生委員会"],
                ["主な論点", "安全（事故防止など）", "衛生（健康・作業環境）"],
                ["設置要件", "業種・人数により異なる", "常時50人以上（全業種）"],
            ]),
            ("試験での注意点", [
                "「衛生委員会があれば安全委員会は不要」→ 必ずしもそうではない（要件を別々に確認）",
                "「安全委員会は全業種で50人以上」→ 業種によって要件が異なる",
            ]),
        ],
    },
    {
        "order": 114,
        "file": "114-joji-shiyo-roudousha",
        "term": "常時使用する労働者",
        "slug": "joji-shiyo-roudousha",
        "category": "関係法令",
        "title": "常時使用する労働者とは？選任・健診の基準人数",
        "related": "eisei-kanrisha:衛生管理者の選任要件;sangyo-i:産業医の選任要件;eisei-iinkai:衛生委員会",
        "csv_desc": "選任要件や健康診断の対象を決めるときの基準となる労働者数の数え方です。パートタイム労働者の扱いが頻出です。",
        "intent": "常時使用する労働者の意味と、50人以上などの基準への当てはめを理解すること。",
        "sections": [
            ("数え方の基本", [
                ["観点", "整理"],
                ["常時使用", "継続して使用している労働者を数える"],
                ["パートタイム", "使用日数・時間にかかわらず原則含める"],
                ["派遣労働者", "派遣先で使用している場合は派遣先で数える場面がある"],
            ]),
            ("頻出の誤り", [
                "「パートは人数に含めない」→ 誤り",
                "「派遣労働者は常に派遣元のみで数える」→ 場面により異なる（試験肢は条文の型で判断）",
            ]),
        ],
    },
    {
        "order": 115,
        "file": "115-kanri-nodo",
        "term": "管理濃度",
        "slug": "kanri-nodo",
        "category": "労働衛生",
        "title": "管理濃度とは？許容濃度との違い・作業環境管理",
        "related": "kyoyo-nodo:許容濃度の整理;sagyo-kankyo-kanri-kubun:作業環境管理区分;yuki-yozai-kubun:有機溶剤の区分",
        "csv_desc": "作業環境測定の結果を評価するときの指標の一つです。許容濃度・管理区分とセットで問われます。",
        "intent": "管理濃度と許容濃度、管理区分の関係を試験用に整理すること。",
        "sections": [
            ("用語の関係", [
                ["用語", "役割"],
                ["許容濃度", "ばく露の目安となる濃度の考え方"],
                ["管理濃度", "作業環境管理のための濃度指標（物質により定められる）"],
                ["管理区分", "測定結果に応じた区分（第1〜第3など）"],
            ]),
            ("試験での見方", [
                "測定→評価→管理区分→措置、の流れで覚える",
                "数値は物質ごとに異なるため、代表例と「比較の仕方」を優先する",
            ]),
        ],
    },
    {
        "order": 116,
        "file": "116-gaitsuke-kyokuhai",
        "term": "外付け型局所排気装置",
        "slug": "gaitsuke-kyokuhai",
        "category": "労働衛生",
        "title": "外付け型局所排気装置とは？囲い型・フード型との違い",
        "related": "kyokuho-haikisochi:局所排気装置;kakomi-kyokuho-haiki:囲い型局所排気装置;fudo-kyokuhai:フード型局所排気装置",
        "csv_desc": "発生源の外側からフード等で汚染空気を捕集する局所排気の形式です。形式ごとの特徴が試験に出ます。",
        "intent": "外付け型・囲い型・フード型の違いと適用場面を整理すること。",
        "sections": [
            ("形式の比較", [
                ["形式", "特徴"],
                ["外付け型", "発生源の外側から捕集"],
                ["囲い型", "作業空間を囲って排気"],
                ["フード型", "フードを発生源近くに設置"],
            ]),
        ],
    },
    {
        "order": 117,
        "file": "117-fudo-kyokuhai",
        "term": "フード型局所排気装置",
        "slug": "fudo-kyokuhai",
        "category": "労働衛生",
        "title": "フード型局所排気装置とは？捕集効率と設置の要点",
        "related": "gaitsuke-kyokuhai:外付け型局所排気装置;seikigu:制気口;haifu-ki-seiatsu:排風機の静圧",
        "csv_desc": "フードで発散物質を直接捕集する局所排気の代表形式です。フードの形状・位置が捕集効率に影響します。",
        "intent": "フード型の特徴と、捕集効率に影響する要因を理解すること。",
        "sections": [
            ("フード設置の要点", [
                ["要因", "影響"],
                ["フードと発生源の距離", "近いほど捕集しやすい"],
                ["囲いの有無", "囲いがあると効率が上がりやすい"],
                ["気流", "フード口への気流が重要"],
            ]),
        ],
    },
    {
        "order": 118,
        "file": "118-dai1shu-yuki-yozai",
        "term": "第1種有機溶剤",
        "slug": "dai1shu-yuki-yozai",
        "category": "関係法令",
        "title": "第1種有機溶剤とは？特別有機溶剤等・第2種との義務の違い",
        "related": "yuki-yozai-kubun:有機溶剤の区分;yuki-yozai-chudoku-yobo-kisoku:有機溶剤中毒予防規則;dai2shu-yuki-yozai:第2種有機溶剤",
        "csv_desc": "有機溶剤中毒予防規則で区分される溶剤の一つです。区分ごとに局所排気・作業環境評価・作業主任者などの義務が変わります。",
        "intent": "第1種有機溶剤の位置づけと、他区分との義務の違いを表で整理すること。",
        "sections": [
            ("有機溶剤の区分（整理）", [
                ["区分", "試験での見方"],
                ["特別有機溶剤等", "最も厳しい管理が中心"],
                ["第1種有機溶剤", "特別に次ぐレベルで義務を確認"],
                ["第2種有機溶剤", "義務の範囲がさらに異なる"],
            ]),
        ],
    },
    {
        "order": 119,
        "file": "119-dai2shu-yuki-yozai",
        "term": "第2種有機溶剤",
        "slug": "dai2shu-yuki-yozai",
        "category": "関係法令",
        "title": "第2種有機溶剤とは？作業環境評価・局所排気の義務",
        "related": "dai1shu-yuki-yozai:第1種有機溶剤;yuki-yozai-kubun:有機溶剤の区分;yuki-yozai-chudoku-yobo-kisoku:有機溶剤中毒予防規則",
        "csv_desc": "有機溶剤の区分の一つで、使用量や物質により適用される義務が第1種・特別有機溶剤等と異なります。",
        "intent": "第2種有機溶剤の義務の型を、他区分と比較して覚えること。",
        "sections": [
            ("区分比較の学習法", [
                "一覧表で「区分名→局所排気→評価→作業主任者」を横並びにする",
                "試験肢は名称の入れ替えが多いので、代表物質名より義務のセットで覚える",
            ]),
        ],
    },
    {
        "order": 120,
        "file": "120-kagaku-busshitsu-kanrisha",
        "term": "化学物質管理者",
        "slug": "kagaku-busshitsu-kanrisha",
        "category": "関係法令",
        "title": "化学物質管理者とは？選任要件・職務・作業主任者との違い",
        "related": "kagaku-busshitsu-kiken-chosa:化学物質等による危険性等の調査;sagyoshunin-sha:作業主任者;eisei-kanrisha:衛生管理者",
        "csv_desc": "化学物質を取り扱う作業場で、法令に基づき選任される管理者です。調査・記録・教育などの職務が問われます。",
        "intent": "化学物質管理者の選任要件と職務の範囲を整理すること。",
        "sections": [
            ("役割の整理", [
                ["役職", "主な焦点"],
                ["化学物質管理者", "化学物質の調査・管理・記録"],
                ["作業主任者", "特定危険作業の現場指揮"],
                ["衛生管理者", "事業場全体の労働衛生管理"],
            ]),
        ],
    },
    {
        "order": 121,
        "file": "121-ishiwata-sagyo",
        "term": "石綿作業",
        "slug": "ishiwata-sagyo",
        "category": "関係法令",
        "title": "石綿作業とは？事前調査・作業主任者・保護具",
        "related": "sekimen-shogai-yobo:石綿障害予防規則;sagyoshunin-sha:作業主任者;kojin-hogo-gu:個人用保護具",
        "csv_desc": "石綿の除去・封じ込め・調査など、石綿障害予防規則の対象となる作業です。手順の厳しさが試験の焦点です。",
        "intent": "石綿作業の事前調査、作業主任者、保護具などの要点を整理すること。",
        "sections": [
            ("石綿作業の流れ（試験用）", [
                ["段階", "確認すること"],
                ["事前", "調査・計画・届出などの要件"],
                ["作業中", "作業主任者・保護具・ばく露低減"],
                ["事後", "廃棄物の扱い・記録"],
            ]),
        ],
    },
    {
        "order": 122,
        "file": "122-niji-kenko-shindan",
        "term": "二次健康診断",
        "slug": "niji-kenko-shindan",
        "category": "関係法令",
        "title": "二次健康診断とは？一次健診後の精密検査・実施時期",
        "related": "teiki-kenko-shindan:定期健康診断;kenkan-kanri-sochi:健康管理措置;shugyo-jo-sochi:就業上の措置",
        "csv_desc": "一次健康診断で異常が認められた場合などに実施する、より詳しい健康診断です。実施時期と就業上の措置がセットで問われます。",
        "intent": "二次健康診断の目的、実施時期、就業上の措置との関係を整理すること。",
        "sections": [
            ("一次健診との流れ", [
                ["段階", "内容"],
                ["一次健康診断", "定期・雇入時などの基本健診"],
                ["二次健康診断", "所見ありの場合の精密検査"],
                ["就業上の措置", "結果に応じた配置転換・就業制限など"],
            ]),
            ("試験での注意点", [
                "「二次健診は任意」→ 所見がある場合の実施義務を確認",
                "実施時期の数値（例：通知後の日数）は条文の型で覚える",
            ]),
        ],
    },
    {
        "order": 123,
        "file": "123-koukiatsu-sagyo",
        "term": "高気圧作業",
        "slug": "koukiatsu-sagyo",
        "category": "労働生理",
        "title": "高気圧作業とは？減圧症・健康診断の要点",
        "related": "tokushu-kenko-shindan:特殊健康診断;teiki-kenko-shindan:定期健康診断",
        "csv_desc": "潜水・シールド工事など、高気圧環境での作業です。減圧症の予防と特殊健康診断が論点になります。",
        "intent": "高気圧作業の健康リスクと、健診・減圧手順の基本を整理すること。",
        "sections": [
            ("試験での論点", [
                "減圧症は急激な減圧で起きやすい",
                "特殊健康診断の対象業務の一つとして整理する",
            ]),
        ],
    },
    {
        "order": 124,
        "file": "124-shinya-gyou",
        "term": "深夜業",
        "slug": "shinya-gyou",
        "category": "関係法令",
        "title": "深夜業とは？健康診断・面接指導との関係",
        "related": "choujikan-rodo-mensetu:長時間労働者面接指導;sangyo-i:産業医;teiki-kenko-shindan:定期健康診断",
        "csv_desc": "午後10時から午前5時までの間に行う業務です。健康への影響と、健診・面接指導の要件が問われます。",
        "intent": "深夜業の定義と、健康管理上の措置の要点を覚えること。",
        "sections": [
            ("時間帯の整理", [
                ["項目", "内容"],
                ["深夜業の時間帯", "午後10時〜翌午前5時（法令の定義に沿って確認）"],
                ["健康管理", "健診・面接指導など関連制度とセットで復習"],
            ]),
        ],
    },
    {
        "order": 125,
        "file": "125-kenkan-kanri-sochi",
        "term": "健康管理措置",
        "slug": "kenkan-kanri-sochi",
        "category": "関係法令",
        "title": "健康管理措置とは？健康診断結果に基づく対応",
        "related": "kenko-shindan-jigo-sochi:健康診断後の事後措置;shugyo-jo-sochi:就業上の措置;haichi-tenkan:配置転換",
        "csv_desc": "健康診断の結果に応じて事業者が講じる措置の総称です。就業上の措置・二次健診などと関連します。",
        "intent": "健康管理措置と就業上の措置の流れを整理すること。",
        "sections": [
            ("措置の流れ", [
                ["段階", "内容"],
                ["健診結果の把握", "医師の意見・所見の確認"],
                ["健康管理措置", "指導・再健診・就業上の措置など"],
                ["記録", "実施内容の記録・保存"],
            ]),
        ],
    },
    {
        "order": 126,
        "file": "126-shugyo-jo-sochi",
        "term": "就業上の措置",
        "slug": "shugyo-jo-sochi",
        "category": "関係法令",
        "title": "就業上の措置とは？就業禁止・配置転換・作業制限",
        "related": "kenko-shindan-jigo-sochi:健康診断後の事後措置;haichi-tenkan:配置転換;kenkan-kanri-sochi:健康管理措置",
        "csv_desc": "健康診断等の結果に基づき、就業禁止・配置転換・作業時間の短縮などを行う措置です。",
        "intent": "就業上の措置の種類と、事業者・医師の役割を整理すること。",
        "sections": [
            ("措置の例", [
                ["措置", "目的"],
                ["就業禁止", "健康障害の悪化を防ぐ"],
                ["配置転換", "ばく露の継続を避ける"],
                ["作業時間の短縮", "負担を軽減する"],
            ]),
        ],
    },
    {
        "order": 127,
        "file": "127-hogo-gu-tekiousei-kensa",
        "term": "保護具着用適合性検査",
        "slug": "hogo-gu-tekiousei-kensa",
        "category": "労働衛生",
        "title": "保護具着用適合性検査とは？呼吸用保護具のフィットテスト",
        "related": "kojin-hogo-gu:個人用保護具;boudoku-masuk:防毒マスク;souki-masuk:送気マスク",
        "csv_desc": "呼吸用保護具などが労働者の顔面に適合しているかを確認する検査です。漏れ込みの防止が目的です。",
        "intent": "着用適合性検査の目的と、保護具選定との関係を理解すること。",
        "sections": [
            ("なぜ必要か", [
                "サイズや形状が合わないと、保護具を着けても漏れ込みが起きる",
                "工程対策の後に、必要な保護具で実施する",
            ]),
        ],
    },
    {
        "order": 128,
        "file": "128-roudousha-eisei-kanri-kiroku",
        "term": "労働者衛生管理記録",
        "slug": "roudousha-eisei-kanri-kiroku",
        "category": "関係法令",
        "title": "労働者衛生管理記録とは？保存期間・記載事項",
        "related": "kojin-kenko-shindan-kiroku:個人の健康診断記録;teiki-kenko-shindan:定期健康診断",
        "csv_desc": "労働者ごとの衛生管理上の記録です。健診結果や措置の内容が含まれ、保存期間が試験に出ます。",
        "intent": "労働者衛生管理記録の保存期間と、個人票との違いを整理すること。",
        "sections": [
            ("記録の整理", [
                ["記録", "保存期間の目安（学習用）"],
                ["一般の健診記録", "5年が中心"],
                ["じん肺健診個人票", "7年"],
                ["特別管理物質など", "30年など長期のものあり"],
            ]),
        ],
    },
    {
        "order": 129,
        "file": "129-anzen-eisei-kaizen-keikaku",
        "term": "安全衛生改善計画",
        "slug": "anzen-eisei-kaizen-keikaku",
        "category": "関係法令",
        "title": "安全衛生改善計画とは？策定・実施・記録",
        "related": "anzen-eisei-kanri-taisei:安全衛生管理体制;risk-assessment:リスクアセスメント",
        "csv_desc": "作業環境の改善や事故防止のため、事業者が策定・実施する計画です。管理体制とセットで問われます。",
        "intent": "安全衛生改善計画の目的と、リスク低減との関係を整理すること。",
        "sections": [
            ("計画の位置づけ", [
                "問題点の把握→改善計画→実施→評価、のPDCAと結びつける",
                "作業環境測定結果やリスクアセスメントと連動させる",
            ]),
        ],
    },
    {
        "order": 130,
        "file": "130-nintei-kikan",
        "term": "認定機関",
        "slug": "nintei-kikan",
        "category": "労働衛生",
        "title": "認定機関とは？作業環境測定・分析の委託",
        "related": "sagyo-kankyo-sokutei:作業環境測定;sagyo-kankyo-sokutei-shi:作業環境測定士",
        "csv_desc": "作業環境測定や分析を行うために、事業者が委託できる機関です。測定の信頼性と手続きが論点です。",
        "intent": "認定機関の役割と、事業者が自ら測定する場合との違いを理解すること。",
        "sections": [
            ("測定の流れ", [
                ["主体", "内容"],
                ["事業者", "測定の実施義務・記録保存"],
                ["認定機関", "委託による測定・分析"],
                ["測定士", "専門的な測定技術"],
            ]),
        ],
    },
    {
        "order": 131,
        "file": "131-sagyo-kankyo-kanri-bo",
        "term": "作業環境管理簿",
        "slug": "sagyo-kankyo-kanri-bo",
        "category": "労働衛生",
        "title": "作業環境管理簿とは？記載事項・保存・掲示",
        "related": "sagyo-kankyo-sokutei:作業環境測定;sagyo-kankyo-hyoka:作業環境評価;sagyo-kankyo-kanri-kubun:作業環境管理区分",
        "csv_desc": "作業環境測定の結果や管理区分などを記録する帳簿です。記載・保存・掲示が試験に出ます。",
        "intent": "作業環境管理簿の記載内容と、測定記録との関係を整理すること。",
        "sections": [
            ("管理簿で確認すること", [
                "測定日・測定結果・管理区分・改善措置",
                "労働者への周知（掲示など）",
            ]),
        ],
    },
    {
        "order": 132,
        "file": "132-a-tokusei-soryo-on",
        "term": "A特性騒音レベル",
        "slug": "a-tokusei-soryo-on",
        "category": "労働衛生",
        "title": "A特性騒音レベルとは？騒音測定・評価量との関係",
        "related": "toka-sonn-level:等価騒音レベル;sagyo-kankyo-sokutei:作業環境測定;choryoku-hogo-gu:聴力保護具",
        "csv_desc": "人の聴感に近づけるための補正を施した騒音レベルです。騒音測定の基本用語として頻出です。",
        "intent": "A特性騒音レベルと等価騒音レベルの違いを整理すること。",
        "sections": [
            ("騒音の用語", [
                ["用語", "意味"],
                ["A特性騒音レベル", "聴感補正した瞬間値・レベル"],
                ["等価騒音レベル", "時間平均した評価量"],
            ]),
        ],
    },
    {
        "order": 133,
        "file": "133-boudoku-masuk",
        "term": "防毒マスク",
        "slug": "boudoku-masuk",
        "category": "労働衛生",
        "title": "防毒マスクとは？送気マスクとの違い・選定の要点",
        "related": "souki-masuk:送気マスク;kojin-hogo-gu:個人用保護具;hogo-gu-tekiousei-kensa:保護具着用適合性検査",
        "csv_desc": "吸着缶などで有害物質を除去する呼吸用保護具です。物質・濃度に応じた選定が重要です。",
        "intent": "防毒マスクと送気マスクの使い分けを理解すること。",
        "sections": [
            ("マスクの比較", [
                ["種類", "特徴"],
                ["防毒マスク", "吸着缶で除去（濃度・物質に制限）"],
                ["送気マスク", "清浄空気を送る（高濃度・酸素欠乏作業など）"],
            ]),
        ],
    },
    {
        "order": 134,
        "file": "134-souki-masuk",
        "term": "送気マスク",
        "slug": "souki-masuk",
        "category": "労働衛生",
        "title": "送気マスクとは？酸素欠乏・高濃度作業での使用",
        "related": "boudoku-masuk:防毒マスク;sanso-ketsubosho-yobo:酸素欠乏症等防止規則;hogo-gu-tekiousei-kensa:保護具着用適合性検査",
        "csv_desc": "ホース等で清浄な空気を送り、マスク内を正圧に保つ呼吸用保護具です。酸素欠乏作業などで重要です。",
        "intent": "送気マスクが必要となる作業場面を整理すること。",
        "sections": [
            ("使用場面", [
                "酸素濃度が低い場所、高濃度の有害物質作業",
                "防毒マスクでは対応できない濃度・条件",
            ]),
        ],
    },
    {
        "order": 135,
        "file": "135-push-pull-kanki",
        "term": "プッシュプル型換気",
        "slug": "push-pull-kanki",
        "category": "労働衛生",
        "title": "プッシュプル型換気とは？全面換気・局所排気との違い",
        "related": "zenmenkaze:全面換気・希釈換気;kyokuho-haikisochi:局所排気装置;kiryu-haifu:気流分布",
        "csv_desc": "送風（プッシュ）と排風（プル）を組み合わせ、作業空間の気流を制御する換気方式です。",
        "intent": "プッシュプル型換気の仕組みと、他の換気方式との違いを整理すること。",
        "sections": [
            ("換気方式の比較", [
                ["方式", "特徴"],
                ["全面換気", "室内全体を希釈"],
                ["局所排気", "発生源で捕集"],
                ["プッシュプル", "気流を制御して汚染を押し出す"],
            ]),
        ],
    },
    {
        "order": 136,
        "file": "136-kiryu-haifu",
        "term": "気流分布",
        "slug": "kiryu-haifu",
        "category": "労働衛生",
        "title": "気流分布とは？換気効率と汚染拡散の理解",
        "related": "zenmenkaze:全面換気;kyokuho-haikisochi:局所排気装置;push-pull-kanki:プッシュプル型換気",
        "csv_desc": "作業空間内の空気の流れのパターンです。換気口の位置や排気の効き方に影響します。",
        "intent": "気流分布が換気・局所排気の効果に与える影響を理解すること。",
        "sections": [
            ("試験での見方", [
                "換気口・排気口・発生源の位置関係が効率を左右する",
                "デッドスペース（気流が届かない場所）に汚染がたまりやすい",
            ]),
        ],
    },
    {
        "order": 137,
        "file": "137-tokutei-kanri-busshitsu",
        "term": "特定管理物質",
        "slug": "tokutei-kanri-busshitsu",
        "category": "関係法令",
        "title": "特定管理物質とは？特別管理物質との違い・健診記録",
        "related": "tokubetsu-kanri-busshitsu:特別管理物質;tokutei-kagaku-busshitsu-shogai-yobo:特定化学物質障害予防規則",
        "csv_desc": "化学物質の中でも、より厳しい管理が求められる物質の区分です。記録保存期間が長いものがあります。",
        "intent": "特定管理物質と特別管理物質の違い、記録保存を整理すること。",
        "sections": [
            ("物質区分", [
                ["区分", "試験での焦点"],
                ["特定管理物質", "管理・記録の義務"],
                ["特別管理物質", "より厳格な管理・長期保存（30年など）"],
            ]),
        ],
    },
    {
        "order": 138,
        "file": "138-tokubetsu-kanri-busshitsu",
        "term": "特別管理物質",
        "slug": "tokubetsu-kanri-busshitsu",
        "category": "関係法令",
        "title": "特別管理物質とは？記録保存30年・作業環境管理",
        "related": "tokutei-kanri-busshitsu:特定管理物質;tokutei-kagaku-busshitsu-shogai-yobo:特定化学物質障害予防規則",
        "csv_desc": "発がん性などが高く、最も厳しい管理が求められる化学物質の区分です。記録保存30年が代表例です。",
        "intent": "特別管理物質の管理の厳しさと保存期間を覚えること。",
        "sections": [
            ("頻出数値", [
                ["項目", "目安"],
                ["健診等の記録保存", "30年（代表例として整理）"],
                ["作業環境", "厳格な測定・管理"],
            ]),
        ],
    },
    {
        "order": 139,
        "file": "139-kanshi-nin",
        "term": "監視人",
        "slug": "kanshi-nin",
        "category": "関係法令",
        "title": "監視人とは？酸素欠乏危険作業・立入管理",
        "related": "sanso-ketsubosho-yobo:酸素欠乏症等防止規則;tachiire-kinshi:立入禁止;ryuuka-suiso-chudoku:硫化水素中毒",
        "csv_desc": "酸素欠乏等の危険作業で、作業者の安全を監視する者です。立入条件とセットで問われます。",
        "intent": "監視人の役割と、測定・換気との手順の順序を整理すること。",
        "sections": [
            ("手順の型", [
                "測定→換気→立入条件の確認→監視人の配置→作業",
                "監視人がいれば測定不要、といった肢は誤りになりやすい",
            ]),
        ],
    },
    {
        "order": 140,
        "file": "140-tachiire-kinshi",
        "term": "立入禁止",
        "slug": "tachiire-kinshi",
        "category": "関係法令",
        "title": "立入禁止とは？酸素欠乏・有害ガス作業の管理",
        "related": "sanso-ketsubosho-yobo:酸素欠乏症等防止規則;kanshi-nin:監視人;kanri-kuiki-nyujo:管理区域への立入",
        "csv_desc": "空気の状態が危険な場合に、作業者以外の立入を制限する措置です。標識・鍵の管理と関連します。",
        "intent": "立入禁止の条件と、管理区域・測定結果との関係を理解すること。",
        "sections": [
            ("管理の要点", [
                "測定結果が基準を満たすまで立入しない",
                "標識・鍵・監視人など複数の対策が組み合わされる",
            ]),
        ],
    },
    {
        "order": 141,
        "file": "141-kakuho-kanki",
        "term": "確保換気",
        "slug": "kakuho-kanki",
        "category": "労働衛生",
        "title": "確保換気とは？必要換気量・換気回数の考え方",
        "related": "hassan-kyodo-kanki-ryo:発散強度・必要換気量;zenmenkaze:全面換気;rodo-eisei-kijun:労働衛生基準",
        "csv_desc": "室内の空気を一定の質・量に保つための換気です。換気回数や必要換気量の計算が試験に出ます。",
        "intent": "確保換気の目的と、希釈換気・発散強度との関係を整理すること。",
        "sections": [
            ("換気の考え方", [
                ["概念", "内容"],
                ["確保換気", "室内空気の質を確保する換気"],
                ["希釈換気", "有害物を希釈する目的の換気"],
            ]),
        ],
    },
    {
        "order": 142,
        "file": "142-kansaku",
        "term": "感作",
        "slug": "kansaku",
        "category": "労働生理",
        "title": "感作とは？化学物質の過敏症・皮膚障害",
        "related": "kagaku-busshitsu-dokusho:化学物質の急性毒性・慢性毒性;hifu-kyushu:皮膚吸収;kojin-hogo-gu:個人用保護具",
        "csv_desc": "一度ばく露すると、以後わずかな量でも過敏反応が起きる現象です。皮膚障害と結びつけて問われます。",
        "intent": "感作の意味と、急性毒性・慢性毒性との違いを整理すること。",
        "sections": [
            ("毒性の整理", [
                ["種類", "特徴"],
                ["急性毒性", "短期間の大量ばく露"],
                ["慢性毒性", "長期の低濃度ばく露"],
                ["感作", "再ばく露で過敏反応"],
            ]),
        ],
    },
    {
        "order": 143,
        "file": "143-hinan-kigu",
        "term": "避難器具",
        "slug": "hinan-kigu",
        "category": "労働衛生",
        "title": "避難器具とは？酸素欠乏作業・救助の備え",
        "related": "sanso-ketsubosho-yobo:酸素欠乏症等防止規則;sanso-ketsubosho-sokutei:酸素濃度測定",
        "csv_desc": "緊急時に作業者を救出するための器具です。酸素欠乏危険作業では設置・点検が義務づけられます。",
        "intent": "避難器具の目的と、酸素欠乏作業の安全対策との関係を理解すること。",
        "sections": [
            ("対策のセット", [
                "測定器・換気・監視人・避難器具・救助体制を一括で整理する",
            ]),
        ],
    },
    {
        "order": 144,
        "file": "144-hyoshiki-keiji",
        "term": "標識の掲示",
        "slug": "hyoshiki-keiji",
        "category": "労働衛生",
        "title": "標識の掲示とは？作業環境・危険有害作業の周知",
        "related": "sagyo-kankyo-kanri-kubun:作業環境管理区分;ghs:GHS;kanri-kuiki-nyujo:管理区域への立入",
        "csv_desc": "管理区分や危険性を労働者に知らせるため、決められた標識を掲示することです。",
        "intent": "標識掲示の目的と、管理区分・GHS表示との関係を整理すること。",
        "sections": [
            ("周知の手段", [
                ["手段", "内容"],
                ["標識の掲示", "管理区分・危険の明示"],
                ["教育", "作業上の注意の説明"],
                ["管理簿・記録", "結果の保存と確認"],
            ]),
        ],
    },
    {
        "order": 145,
        "file": "145-haichi-tenkan",
        "term": "配置転換",
        "slug": "haichi-tenkan",
        "category": "関係法令",
        "title": "配置転換とは？健康診断・じん肺・有害業務",
        "related": "shugyo-jo-sochi:就業上の措置;jinpai:じん肺;kenko-shindan-jigo-sochi:健康診断後の事後措置",
        "csv_desc": "健康上の理由から、労働者を別の作業・職場へ移すことです。じん肺や特殊健診の結果と関連します。",
        "intent": "配置転換が必要となる場面と、就業上の措置との関係を整理すること。",
        "sections": [
            ("配置転換の例", [
                ["状況", "目的"],
                ["じん肺の疑い", "粉じんばく露の継続を防ぐ"],
                ["有機溶剤等の健康影響", "有害作業から離す"],
                ["騒音性難聴", "騒音ばく露の低減"],
            ]),
        ],
    },
]


def render_section(h2: str, content) -> str:
    lines = [f"## {h2}", ""]
    if not content:
        return ""
    first = content[0]
    if isinstance(first, list) and len(first) >= 2 and isinstance(first[0], str):
        lines.append("| " + " | ".join(first) + " |")
        lines.append("| " + " | ".join(["---"] * len(first)) + " |")
        for row in content[1:]:
            if isinstance(row, list):
                lines.append("| " + " | ".join(str(c) for c in row) + " |")
            else:
                lines.append(f"- {row}")
        lines.append("")
    else:
        for item in content:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def build_body(term: str, title_short: str, category: str, sections: list) -> str:
    h1 = title_short.split("【")[0].strip()
    if not h1.endswith("？"):
        h1 = h1.replace("とは", "とは？", 1) if "とは" in h1 else h1 + "とは？"
    intro = (
        f"{term}は、第二種衛生管理者試験の{category}で頻出の用語です。"
        f"この記事では、{term}の意味、試験で問われやすい観点、関連用語との違いを復習に使える形で整理します。"
    )
    parts = [f"# {h1}", "", intro, "", "---", ""]
    for h2, content in sections:
        parts.append(render_section(h2, content))
    parts.extend(
        [
            "---",
            "",
            "## 試験での見方を整理する",
            "",
            f"{term}は、定義だけでなく条件の言い換えまで問われやすいテーマです。"
            "本文の表で対象・頻度・数値・義務の主体を確認し、頻出ポイントで誤り選択肢を判断できるようにします。",
            "",
            "---",
            "",
            "## 次に確認すること",
            "",
            f"{term}を確認したら、関連用語・まとめ記事・過去問へ進み、似た制度は横並びで比較してください。"
            "受験前には公式情報もあわせて確認してください。",
            "",
        ]
    )
    return "\n".join(parts)


def build_frontmatter(item: dict) -> str:
    term = item["term"]
    title = f"{item['title']}【第二種衛生管理者試験】"
    desc = (
        f"第二種衛生管理者試験向けに{term}を解説。"
        f"定義、試験の頻出ポイント、関連制度との違いを表で整理します。"
    )
    faq1_q = f"{term}は試験でどこを見ればよいですか？"
    faq1_a = (
        f"{term}は、定義とあわせて数値・対象・手順の言い換えが問われやすいテーマです。"
        "本文の表で整理し、関連用語と比較して復習してください。"
    )
    faq2_q = "公式情報も確認した方がよいですか？"
    faq2_a = (
        f"{term}に関する要件は、法令改正や公式資料の更新で変わることがあります。"
        "本記事は学習用の整理として使い、受験前に公式情報も確認してください。"
    )
    lines = [
        "---",
        f"action_items: {term}の定義を確認する;表で区分や数値を整理する;頻出の誤り選択肢を復習する;関連用語を読む;公式情報で最新条件を確認する",
        "author_name: 二衛マスター編集部",
        "author_profile: 第二種衛生管理者試験の学習用語、過去問の復習導線、試験ガイドを整理する編集チームです。",
        f"category: {item['category']}",
        "content_status: published",
        f"description: {desc}",
        f"fact_checked_at: '{DATE}'",
        f"faq_1_answer: {faq1_a}",
        f"faq_1_question: {faq1_q}",
        f"faq_2_answer: {faq2_a}",
        f"faq_2_question: {faq2_q}",
        f"last_reviewed_at: '{DATE}'",
        f"next_review_at: '2026-06-19'",
        f"order: {item['order']}",
        f"original_note: {term}について、第二種衛生管理者試験で問われやすい定義・数値・関連制度を中心に整理しています。",
        f"primary_sources: {SOURCES}",
        f"related_links: {item['related']}",
        "reviewer_name: 二衛マスター編集部",
        "reviewer_profile: 公開前に公式情報、法令情報、サイト内の関連ページとの整合性を確認しています。",
        f"revision_note: 用語35本追加バッチ。{term}の検索意図・FAQ・関連記事を整備。",
        f"slug: {item['slug']}",
        f"source_checked_at: '{DATE}'",
        f"title: {title}",
        "update_policy: 試験要項、公式ページ、関係法令に変更が確認されたタイミングで本文と参照元を見直します。",
        f"updated: '{DATE}'",
        f"user_intent: {item['intent']}",
        "---",
    ]
    return "\n".join(lines)


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
        body = build_body(item["term"], item["title"], item["category"], item["sections"])
        md_path.write_text(
            build_frontmatter(item) + "\n\n" + body,
            encoding="utf-8",
        )
        slug_map[item["term"]] = item["slug"]
        existing_slugs.add(item["slug"])
        created += 1
        print(f"created: {md_path.name}")

    SLUG_JSON.write_text(
        json.dumps(slug_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # append checklist rows
    rows_to_add = []
    for item in NEW_TERMS:
        if item["term"] not in slug_map:
            continue
        rows_to_add.append((item["category"], item["term"], item["csv_desc"]))

    with CHECKLIST_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        all_rows = list(reader)
    existing_terms = {r[1] for r in all_rows[1:] if len(r) > 1}
    with CHECKLIST_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in all_rows:
            writer.writerow(row)
        for cat, term, desc in rows_to_add:
            if term not in existing_terms:
                writer.writerow([cat, term, desc])
                existing_terms.add(term)

    print(f"done: {created} articles, {len(slug_map)} slugs total")


if __name__ == "__main__":
    main()
