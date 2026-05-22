#!/usr/bin/env python3
"""用語・詳細記事 第4弾50本追加（217〜266）。過去問頻出・試験重要語を優先。"""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTICLES = REPO / "eisei-articles" / "articles"
SLUG_JSON = REPO / "docs" / "glossary-article-slugs.json"
CHECKLIST_CSV = REPO / "docs" / "glossary-terms-checklist.csv"
GLOSSARY_CSV = REPO / "data" / "glossary_terms.csv"
DATE = "2026-05-22"

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
    related_terms_csv: str = "",
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
        "related_terms_csv": related_terms_csv,
    }


def csv_row(item: dict) -> dict[str, str]:
    term = item["term"]
    title = f"{item['title']}【第二種衛生管理者試験】"
    desc = item["csv_desc"]
    related = item.get("related_terms_csv") or ""
    return {
        "term": term,
        "reading": "（読み未登録）",
        "category": item["category"],
        "tags": "第二種衛生管理者",
        "short_def": desc,
        "definition": desc,
        "related_terms": related,
        "legal_basis": "",
        "importance": "A",
        "explanation": desc,
        "article_title": title,
        "article_lead": desc,
        "term_detail_body": desc,
        "exam_points": "",
        "common_mistakes": "",
        "memory_tip": "",
        "example_question": "",
        "example_answer": "",
        "faq_1_question": f"{term}は試験でどこを見ればよいですか？",
        "faq_1_answer": (
            f"{term}は、定義とあわせて数値・対象・手順の言い換えが問われやすいテーマです。"
            "本文の表で整理し、関連用語と比較して復習してください。"
        ),
        "faq_2_question": "公式情報も確認した方がよいですか？",
        "faq_2_answer": (
            f"{term}に関する要件は、法令改正や公式資料の更新で変わることがあります。"
            "本記事は学習用の整理として使い、受験前に公式情報も確認してください。"
        ),
        "slug": item["slug"],
    }


NEW_TERMS: list[dict] = [
    T(
        217,
        "217-kenko-shindan",
        "健康診断",
        "kenko-shindan",
        "関係法令",
        "健康診断とは？種類・実施時期・記録保存を整理",
        "rodo-anzen-eisei-ho:労働安全衛生法;koyounyu-kenko-shindan:雇入時健康診断;tokushu-kenko-shindan:特殊健康診断",
        "労働者の健康状態を把握するための診断の総称です。定期・雇入時・特殊など種類ごとの違いが頻出です。",
        "健康診断の種類と実施時期・記録の違いを選択肢で判断できるようにすること。",
        [
            ("健康診断の種類", [
                ["種類", "主な実施タイミング"],
                ["雇入時健康診断", "雇い入れの際（就業前）"],
                ["定期健康診断", "1年以内ごとに1回"],
                ["特殊健康診断", "有害業務ごと（多くは6か月以内ごとに1回）"],
            ]),
            ("試験で狙われる頻出ポイント", [
                "「健康診断＝定期健康診断のみ」→ 誤り（雇入時・特殊など複数ある）",
                "「異常があっても就業上の措置は不要」→ 事後措置・二次健診の流れを確認",
                "「記録の保存期間はすべて同じ」→ 健診の種類・物質により異なる",
            ]),
        ],
        "労働安全衛生法;雇入時健康診断;特殊健康診断;二次健康診断",
    ),
    T(
        218,
        "218-teiki-kenshin",
        "定期健康診断",
        "teiki-kenshin",
        "関係法令",
        "定期健康診断とは？1年以内・対象・雇入時健診との違い",
        "koyounyu-kenko-shindan:雇入時健康診断;kenko-shindan-jigo-sochi:健康診断の事後措置;niji-kenko-shindan:二次健康診断",
        "常時使用する労働者を対象に、1年以内ごとに1回実施する健康診断です。",
        "定期健康診断の対象・頻度・雇入時健診との違いを整理すること。",
        [
            ("定期健康診断の基本", [
                ["項目", "内容"],
                ["対象", "常時使用する労働者（パートタイム含む）"],
                ["頻度", "1年以内ごとに1回"],
                ["記録", "個人別の健康診断結果等の記録を保存"],
            ]),
            ("雇入時健診との違い", [
                ["項目", "雇入時健康診断", "定期健康診断"],
                ["時期", "雇い入れの際", "継続雇用中"],
                ["回数", "入社時が中心", "1年以内ごとに1回"],
            ]),
        ],
        "雇入時健康診断;健康診断の事後措置;二次健康診断;常時使用する労働者",
    ),
    T(
        219,
        "219-mensetsu-shido",
        "面接指導",
        "mensetsu-shido",
        "関係法令",
        "面接指導とは？長時間労働・産業医・記録保存",
        "choujikan-rodo-mensetu:長時間労働者面接指導;sangyo-i:産業医;stress-check:ストレスチェック制度",
        "健康診断結果等に基づき産業医が行う面接による指導です。長時間労働者への実施が頻出です。",
        "面接指導の実施者・対象・記録保存と長時間労働者面接指導の違いを整理すること。",
        [
            ("面接指導と長時間労働者面接指導", [
                ["項目", "面接指導（一般）", "長時間労働者面接指導"],
                ["実施者", "産業医", "産業医"],
                ["きっかけ", "健診結果等", "月80時間超の時間外労働など"],
            ]),
        ],
        "長時間労働者面接指導;産業医;ストレスチェック制度;時間外労働",
    ),
    T(
        220,
        "220-ichiji-kenko-shindan",
        "一次健康診断",
        "ichiji-kenko-shindan",
        "関係法令",
        "一次健康診断とは？二次健診・異常所見・事後措置",
        "niji-kenko-shindan:二次健康診断;kenko-shindan-jigo-sochi:健康診断の事後措置;shugyo-jo-sochi:就業上の措置",
        "定期健康診断などで最初に行う健康診断です。異常時の二次健診・措置とセットで問われます。",
        "一次と二次健康診断の関係と事後措置の流れを理解すること。",
        related_terms_csv="二次健康診断;健康診断の事後措置;就業上の措置",
    ),
    T(
        221,
        "221-roudou-kijun-kantokusho",
        "労働基準監督署",
        "roudou-kijun-kantokusho",
        "関係法令",
        "労働基準監督署とは？職権・是正勧告・労働安全衛生",
        "rodo-anzen-eisei-ho:労働安全衛生法;jigyosha-ippan-gimu:事業者の一般義務;anzen-eisei-kanri-taisei:安全衛生管理体制",
        "労働基準法・労働安全衛生法の遵守を監督する行政機関です。",
        "監督署の職権と事業者の義務の関係を整理すること。",
        related_terms_csv="労働安全衛生法;事業者の一般義務",
    ),
    T(
        222,
        "222-roudou-eisei-consultant",
        "労働衛生コンサルタント",
        "roudou-eisei-consultant",
        "関係法令",
        "労働衛生コンサルタントとは？選任・業務・衛生管理者との違い",
        "eisei-kanrisha:衛生管理者;sagyo-kankyo-sokutei-shi:作業環境測定士;menkyo-shinsei:免許申請",
        "作業環境測定や衛生管理の専門的助言を行う国家資格者です。",
        "労働衛生コンサルタントと衛生管理者・作業環境測定士の役割の違いを整理すること。",
        related_terms_csv="衛生管理者;作業環境測定士;免許申請",
    ),
    T(
        223,
        "223-menkyo",
        "免許",
        "menkyo",
        "関係法令",
        "免許とは？衛生管理者・作業環境測定士・有効期間",
        "menkyo-shinsei:免許申請;eisei-kanrisha:衛生管理者;sagyo-kankyo-sokutei-shi:作業環境測定士",
        "衛生管理者や作業環境測定士などの国家試験合格後に交付される資格です。",
        "免許の種類と有効期間・更新の考え方を整理すること。",
        related_terms_csv="免許申請;衛生管理者;作業環境測定士",
    ),
    T(
        224,
        "224-anzen-eisei-iinkai",
        "安全衛生委員会",
        "anzen-eisei-iinkai",
        "関係法令",
        "安全衛生委員会とは？設置要件・衛生委員会との違い",
        "anzen-iinkai:安全委員会;eisei-iinkai:衛生委員会;anzen-eisei-kanri-taisei:安全衛生管理体制",
        "安全と衛生の両面について協議する委員会です。設置要件が頻出です。",
        "安全衛生委員会と安全委員会・衛生委員会の違いを整理すること。",
        related_terms_csv="安全委員会;衛生委員会;安全衛生管理体制",
    ),
    T(
        225,
        "225-kagaku-busshitsu",
        "化学物質",
        "kagaku-busshitsu",
        "関係法令",
        "化学物質とは？有害性・管理区分・SDS",
        "sds:SDS（安全データシート）;ghs:GHS（化学品の分類と表示に関する世界調和システム）;tokutei-kagaku-busshitsu-shogai-yobo:特定化学物質障害予防規則",
        "職場で取り扱う化学物質の総称です。有害性調査・リスクアセスメントと関連します。",
        "化学物質の管理とSDS・GHS表示の関係を理解すること。",
        related_terms_csv="SDS（安全データシート）;GHS（化学品の分類と表示に関する世界調和システム）;リスクアセスメント",
    ),
    T(
        226,
        "226-jikangai-roudou",
        "時間外労働",
        "jikangai-roudou",
        "関係法令",
        "時間外労働とは？36協定・長時間労働・面接指導",
        "choujikan-rodo-mensetu:長時間労働者面接指導;mensetsu-shido:面接指導;sangyo-i:産業医",
        "法定労働時間を超える労働です。長時間労働者への措置と関連します。",
        "時間外労働と長時間労働・面接指導の関係を整理すること。",
        related_terms_csv="長時間労働者面接指導;面接指導;産業医",
    ),
    T(
        227,
        "227-koushin-shinkei",
        "交感神経",
        "koushin-shinkei",
        "労働生理",
        "交感神経とは？副交感神経・自律神経・働きの違い",
        "fukukous-shinkei:副交感神経;jiritsu-shinkei:自律神経;taisei-shinkei:体性神経",
        "闘争・逃走反応など身体を活動状態にする神経系の一部です。副交感神経との正反対の働きが頻出です。",
        "交感神経と副交感神経の働きの違いを選択肢で判断できるようにすること。",
        [
            ("交感神経と副交感神経", [
                ["項目", "交感神経", "副交感神経"],
                ["心拍", "増加", "減少"],
                ["消化管運動", "抑制", "亢進"],
                ["状態", "活動・緊張時", "休息・睡眠時"],
            ]),
            ("試験での注意点", [
                "「神経核は末梢、神経節は中枢」→ 逆（神経核＝中枢、神経節＝末梢）",
                "「交感・副交感は同一器官に分布しない」→ 両方分布し作用はほぼ正反対",
            ]),
        ],
        "副交感神経;自律神経;体性神経;神経核;神経節",
    ),
    T(
        228,
        "228-fukukous-shinkei",
        "副交感神経",
        "fukukous-shinkei",
        "労働生理",
        "副交感神経とは？交感神経・休息・消化の亢進",
        "koushin-shinkei:交感神経;jiritsu-shinkei:自律神経;chushou-shinkei:中枢神経系",
        "休息・睡眠時に活動が高まり、心拍減少・消化管運動亢進などをもたらす神経系です。",
        "副交感神経の働きと交感神経との対比を整理すること。",
        related_terms_csv="交感神経;自律神経;体性神経",
    ),
    T(
        229,
        "229-jiritsu-shinkei",
        "自律神経",
        "jiritsu-shinkei",
        "労働生理",
        "自律神経とは？交感・副交感・不随意の調節",
        "koushin-shinkei:交感神経;fukukous-shinkei:副交感神経;taisei-shinkei:体性神経",
        "内臓・血管・腺などを意志とは無関係に調節する神経系です。",
        "自律神経と体性神経の違いを整理すること。",
        related_terms_csv="交感神経;副交感神経;体性神経",
    ),
    T(
        230,
        "230-taisei-shinkei",
        "体性神経",
        "taisei-shinkei",
        "労働生理",
        "体性神経とは？感覚神経・運動神経・自律神経との違い",
        "koushin-shinkei:交感神経;jiritsu-shinkei:自律神経;shinkei-kaku:神経核",
        "随意運動や感覚に関わる神経です。感覚神経と運動神経に分類されます。",
        "体性神経の分類と自律神経との違いを理解すること。",
        related_terms_csv="交感神経;自律神経;神経核",
    ),
    T(
        231,
        "231-shinkei-kaku",
        "神経核",
        "shinkei-kaku",
        "労働生理",
        "神経核とは？神経節・中枢神経系・末梢神経系",
        "shinkei-setsu:神経節;chushou-shinkei:中枢神経系;massho-shinkei:末梢神経系",
        "中枢神経系で神経細胞の細胞体が集まる部位です。神経節との取り違えが頻出です。",
        "神経核と神経節の位置づけの違いを押さえること。",
        [
            ("神経核と神経節", [
                ["項目", "神経核", "神経節"],
                ["位置", "中枢神経系（脳・脊髄）", "末梢神経系"],
                ["内容", "神経細胞体の集合", "神経細胞体の集合"],
            ]),
        ],
        "神経節;中枢神経系;末梢神経系",
    ),
    T(
        232,
        "232-shinkei-setsu",
        "神経節",
        "shinkei-setsu",
        "労働生理",
        "神経節とは？神経核・末梢神経系・取り違え注意",
        "shinkei-kaku:神経核;massho-shinkei:末梢神経系;taisei-shinkei:体性神経",
        "末梢神経系で神経細胞の細胞体が集まる部位です。",
        "神経節と神経核の取り違えに注意して整理すること。",
        related_terms_csv="神経核;末梢神経系;体性神経",
    ),
    T(
        233,
        "233-chushou-shinkei",
        "中枢神経系",
        "chushou-shinkei",
        "労働生理",
        "中枢神経系とは？脳・脊髄・末梢神経系との区分",
        "massho-shinkei:末梢神経系;shinkei-kaku:神経核;daeno:大脳",
        "脳と脊髄からなる神経系です。神経核は中枢、神経節は末梢に位置します。",
        "中枢神経系と末梢神経系の区分を整理すること。",
        related_terms_csv="末梢神経系;神経核;大脳",
    ),
    T(
        234,
        "234-massho-shinkei",
        "末梢神経系",
        "massho-shinkei",
        "労働生理",
        "末梢神経系とは？中枢神経系・神経節・神経核",
        "chushou-shinkei:中枢神経系;shinkei-setsu:神経節;shinkei-kaku:神経核",
        "中枢神経系以外の神経からなる系統です。",
        "末梢神経系の範囲と神経節の位置づけを理解すること。",
        related_terms_csv="中枢神経系;神経節;神経核",
    ),
    T(
        235,
        "235-fukensen-kansen",
        "不顕性感染",
        "fukensen-kansen",
        "労働生理",
        "不顕性感染とは？日和見感染・キャリア・症状なし",
        "nichijomi-kansen:日和見感染;carrier:キャリア;kansen-sho:感染症",
        "感染は成立するが症状が現れない状態です。日和見感染との区別が頻出です。",
        "不顕性感染と日和見感染の定義の違いを整理すること。",
        [
            ("感染関連用語の整理", [
                ["用語", "意味"],
                ["不顕性感染", "感染成立するが症状なし"],
                ["日和見感染", "抵抗力低下時に発症"],
                ["キャリア", "自覚なく病原体を散布しうる者"],
            ]),
        ],
        "日和見感染;キャリア;感染症;病原体",
    ),
    T(
        236,
        "236-nichijomi-kansen",
        "日和見感染",
        "nichijomi-kansen",
        "労働生理",
        "日和見感染とは？抵抗力低下・不顕性感染",
        "fukensen-kansen:不顕性感染;byoukin:病原体;kansen-sho:感染症",
        "抵抗力が低下したときに発症する感染です。",
        "日和見感染の定義と不顕性感染との違いを押さえること。",
        related_terms_csv="不顕性感染;病原体;感染症",
    ),
    T(
        237,
        "237-carrier",
        "キャリア",
        "carrier",
        "労働生理",
        "キャリアとは？感染症・無症状・感染源",
        "fukensen-kansen:不顕性感染;himaku-kansen:飛沫感染;kuuki-kansen:空気感染",
        "感染しているが自覚症状がなく病原体を散布しうる者です。",
        "キャリアの意味と感染経路との関係を整理すること。",
        related_terms_csv="不顕性感染;飛沫感染;空気感染",
    ),
    T(
        238,
        "238-himaku-kansen",
        "飛沫感染",
        "himaku-kansen",
        "労働生理",
        "飛沫感染とは？空気感染・接触感染・5µm",
        "kuuki-kansen:空気感染;sesshoku-kansen:接触感染;byoukin:病原体",
        "飛沫を介した感染経路です。空気感染（小粒子）との違いが問われます。",
        "飛沫感染と空気感染の粒子サイズの違いを整理すること。",
        related_terms_csv="空気感染;接触感染;病原体",
    ),
    T(
        239,
        "239-kuuki-kansen",
        "空気感染",
        "kuuki-kansen",
        "労働生理",
        "空気感染とは？飛沫感染・小粒子・空調",
        "himaku-kansen:飛沫感染;sesshoku-kansen:接触感染;byoukin:病原体",
        "5µm以下の粒子が長時間浮遊して感染する経路です。",
        "空気感染の特徴と飛沫感染との違いを理解すること。",
        related_terms_csv="飛沫感染;接触感染;病原体",
    ),
    T(
        240,
        "240-sesshoku-kansen",
        "接触感染",
        "sesshoku-kansen",
        "労働生理",
        "接触感染とは？飛沫・空気感染・手洗い",
        "himaku-kansen:飛沫感染;kuuki-kansen:空気感染;kansen-sho:感染症",
        "病原体が付着したものに触れて感染する経路です。",
        "接触感染と飛沫・空気感染の違いを整理すること。",
        related_terms_csv="飛沫感染;空気感染;感染症",
    ),
    T(
        241,
        "241-kansen-sho",
        "感染症",
        "kansen-sho",
        "労働生理",
        "感染症とは？病原体・感染経路・予防",
        "byoukin:病原体;fukensen-kansen:不顕性感染;kuuki-kansen:空気感染",
        "病原体による疾病の総称です。感染成立の条件が問われます。",
        "感染症の成立条件と感染経路を整理すること。",
        related_terms_csv="病原体;不顕性感染;空気感染",
    ),
    T(
        242,
        "242-byoukin",
        "病原体",
        "byoukin",
        "労働生理",
        "病原体とは？細菌・ウイルス・感染症",
        "kansen-sho:感染症;fukensen-kansen:不顕性感染;nichijomi-kansen:日和見感染",
        "感染症の原因となる微生物などです。",
        "病原体の種類と感染経路の関係を理解すること。",
        related_terms_csv="感染症;不顕性感染;日和見感染",
    ),
    T(
        243,
        "243-nisanka-tanso",
        "二酸化炭素",
        "nisanka-tanso",
        "労働生理",
        "二酸化炭素とは？酸素欠乏・換気・血中濃度",
        "sanso-ketsubosho:酸素欠乏症;ichisanka-tanso-chudoku:一酸化炭素中毒;taion-chosetsu:体温調節",
        "酸素欠乏の一因となるガスです。換気不足で濃度が上昇します。",
        "二酸化炭素と酸素欠乏・一酸化炭素の違いを整理すること。",
        related_terms_csv="酸素欠乏症;一酸化炭素中毒",
    ),
    T(
        244,
        "244-ichisanka-tanso-gas",
        "一酸化炭素",
        "ichisanka-tanso-gas",
        "労働生理",
        "一酸化炭素とは？中毒・ヘモグロビン・換気",
        "ichisanka-tanso-chudoku:一酸化炭素中毒;carboxy-hemoglobin:カルボキシヘモグロビン（COHb）;sanso-ketsubosho:酸素欠乏症",
        "ヘモグロビンと強く結合し酸素運搬を阻害するガスです。",
        "一酸化炭素中毒のメカニズムを整理すること。",
        related_terms_csv="一酸化炭素中毒;カルボキシヘモグロビン（COHb）;酸素欠乏症",
    ),
    T(
        245,
        "245-fukansen-sho",
        "不感蒸泄",
        "fukansen-sho",
        "労働生理",
        "不感蒸泄とは？発汗・体温調節・温熱環境",
        "hassan:発汗;wbgt:WBGT;necchuysho:熱中症",
        "汗をかかずに行われる蒸発による熱放散です。",
        "不感蒸泄と発汗の違いを整理すること。",
        related_terms_csv="発汗;WBGT;熱中症",
    ),
    T(
        246,
        "246-hassan",
        "発汗",
        "hassan",
        "労働生理",
        "発汗とは？感蒸泄・熱中症・体温調節",
        "fukansen-sho:不感蒸泄;necchuysho:熱中症;wbgt:WBGT",
        "汗の蒸発により熱を放散する体温調節です。",
        "発汗による熱放散と熱中症予防の関係を理解すること。",
        related_terms_csv="不感蒸泄;熱中症;WBGT",
    ),
    T(
        247,
        "247-taisha-ritsu",
        "代謝率",
        "taisha-ritsu",
        "労働生理",
        "代謝率とは？メタボリックレート・発熱量・WBGT",
        "metabolic-rate:メタボリックレート（代謝量）;wbgt:WBGT;necchuysho:熱中症",
        "体内でエネルギーを産生する速度です。温熱環境評価に用います。",
        "代謝率とWBGT・作業強度の関係を整理すること。",
        related_terms_csv="メタボリックレート（代謝量）;WBGT;熱中症",
    ),
    T(
        248,
        "248-daeno",
        "大脳",
        "daeno",
        "労働生理",
        "大脳とは？皮質・感覚・運動・思考",
        "shonen:小脳;chushou-shinkei:中枢神経系;taisei-shinkei:体性神経",
        "感覚・運動・思考などを支配する中枢です。",
        "大脳皮質の機能を整理すること。",
        related_terms_csv="小脳;中枢神経系;体性神経",
    ),
    T(
        249,
        "249-shonen",
        "小脳",
        "shonen",
        "労働生理",
        "小脳とは？随意運動・平衡・運動失調",
        "daeno:大脳;taisei-shinkei:体性神経;chushou-shinkei:中枢神経系",
        "随意運動や平衡機能を調整する中枢です。",
        "小脳の機能と運動失調の関係を理解すること。",
        related_terms_csv="大脳;体性神経;中枢神経系",
    ),
    T(
        250,
        "250-funjin",
        "粉じん",
        "funjin",
        "労働生理",
        "粉じんとは？じん肺・作業環境・呼吸器障害",
        "jinpai:じん肺;ishiwata-funjin:石綿粉じん;funzin-shogai-boshi:粉じん障害防止規則",
        "空気中に浮遊する固体粒子です。じん肺の原因物質として頻出です。",
        "粉じんとじん肺・作業環境管理の関係を整理すること。",
        related_terms_csv="じん肺;石綿粉じん;粉じん障害防止規則",
    ),
    T(
        251,
        "251-ryuukasuiso",
        "硫化水素",
        "ryuukasuiso",
        "労働生理",
        "硫化水素とは？酸素欠乏・臭い・中毒",
        "sanso-ketsubosho-yobo:酸素欠乏症等防止規則;sanso-ketsubosho:酸素欠乏症;ichisanka-tanso-chudoku:一酸化炭素中毒",
        "悪臭のある有毒ガスです。酸素欠乏作業の危険物質として問われます。",
        "硫化水素の危険性と酸素欠乏作業の対策を整理すること。",
        related_terms_csv="酸素欠乏症等防止規則;酸素欠乏症",
    ),
    T(
        252,
        "252-ammonia",
        "アンモニア",
        "ammonia",
        "労働生理",
        "アンモニアとは？刺激性・眼・上気道",
        "enso:塩素;kagaku-busshitsu-dokusho:化学物質の急性毒性・慢性毒性;kojin-hogo-gu:個人用保護具",
        "強い刺激性のあるガスです。",
        "アンモニアの刺激性と保護具の必要性を理解すること。",
        related_terms_csv="塩素;化学物質の急性毒性・慢性毒性;個人用保護具",
    ),
    T(
        253,
        "253-enso",
        "塩素",
        "enso",
        "労働生理",
        "塩素とは？刺激性ガス・中毒・保護具",
        "ammonia:アンモニア;kagaku-busshitsu:化学物質;boudoku-masuk:防毒マスク",
        "黄緑色の刺激性有毒ガスです。",
        "塩素の毒性と呼吸用保護具の選定を整理すること。",
        related_terms_csv="アンモニア;化学物質;防毒マスク",
    ),
    T(
        254,
        "254-yuuki-rin",
        "有機リン",
        "yuuki-rin",
        "労働生理",
        "有機リンとは？農薬・神経毒・胆碱酯酶",
        "yuukisuigin:有機水銀;kagaku-busshitsu-dokusho:化学物質の急性毒性・慢性毒性;byoukin:病原体",
        "農薬等に含まれる神経毒です。胆碱酯酶阻害が特徴です。",
        "有機リン中毒の特徴を整理すること。",
        related_terms_csv="化学物質の急性毒性・慢性毒性;化学物質",
    ),
    T(
        255,
        "255-suigin",
        "水銀",
        "suigin",
        "労働生理",
        "水銀とは？有機水銀・メチル水銀・中毒",
        "yuukisuigin:有機水銀;namari-chudoku-yobo:鉛中毒予防規則;kagaku-busshitsu:化学物質",
        "金属水銀およびその化合物による健康障害の原因物質です。",
        "水銀と有機水銀の毒性の違いを整理すること。",
        related_terms_csv="鉛中毒予防規則;化学物質;化学物質の急性毒性・慢性毒性",
    ),
    T(
        256,
        "256-sekimen",
        "石綿",
        "sekimen",
        "労働生理",
        "石綿とは？アスベスト・石綿障害・ばく露",
        "ishiwata-funjin:石綿粉じん;ishiwata-sagyo:石綿作業;sekimen-shogai-yobo:石綿障害予防規則",
        "アスベストとも呼ばれる繊維状鉱物です。",
        "石綿ばく露と石綿障害予防規則の要点を理解すること。",
        related_terms_csv="石綿粉じん;石綿作業;石綿障害予防規則",
    ),
    T(
        257,
        "257-silica",
        "シリカ",
        "silica",
        "労働生理",
        "シリカとは？結晶質シリカ・粉じん・じん肺",
        "funjin:粉じん;jinpai:じん肺;ishiwata-funjin:石綿粉じん",
        "結晶質シリカによる粉じんはじん肺の重要な原因です。",
        "シリカ粉じんとじん肺の関係を整理すること。",
        related_terms_csv="粉じん;じん肺;石綿粉じん",
    ),
    T(
        258,
        "258-genatsu-sho",
        "減圧症",
        "genatsu-sho",
        "労働生理",
        "減圧症とは？高気圧作業・潜水・関節痛",
        "koukiatsu-sagyo:高気圧作業;tokushu-kenko-shindan:特殊健康診断;sanso-ketsubosho:酸素欠乏症",
        "急激な減圧で体内に溶けたガスが泡となる障害です。",
        "減圧症と高気圧作業の予防を整理すること。",
        related_terms_csv="高気圧作業;特殊健康診断",
    ),
    T(
        259,
        "259-kyusei-dokusei",
        "急性毒性",
        "kyusei-dokusei",
        "労働生理",
        "急性毒性とは？慢性毒性・LD50・化学物質",
        "kagaku-busshitsu-dokusho:化学物質の急性毒性・慢性毒性;hatsugansei:発がん性;ghs:GHS（化学品の分類と表示に関する世界調和システム）",
        "短期間のばく露で現れる毒性です。",
        "急性毒性と慢性毒性の違いを整理すること。",
        related_terms_csv="化学物質の急性毒性・慢性毒性;発がん性;GHS（化学品の分類と表示に関する世界調和システム）",
    ),
    T(
        260,
        "260-mansei-dokusei",
        "慢性毒性",
        "mansei-dokusei",
        "労働生理",
        "慢性毒性とは？急性毒性・長期ばく露",
        "kagaku-busshitsu-dokusho:化学物質の急性毒性・慢性毒性;kyusei-dokusei:急性毒性;hatsugansei:発がん性",
        "長期間のばく露で現れる毒性です。",
        "慢性毒性の意味と発がん性との関係を理解すること。",
        related_terms_csv="化学物質の急性毒性・慢性毒性;急性毒性;発がん性",
    ),
    T(
        261,
        "261-ketsuchu",
        "血中",
        "ketsuchu",
        "労働衛生",
        "血中とは？生物学的モニタリング・鉛・有機溶剤",
        "ketsuchu-noudo:血中濃度;nyouchu:尿中;seibutsugaku-monitoring:生物学的モニタリング",
        "血液中有害物質濃度の測定です。ばく露評価に用います。",
        "血中濃度測定の位置づけを整理すること。",
        related_terms_csv="血中濃度;尿中;生物学的モニタリング",
    ),
    T(
        262,
        "262-nyouchu",
        "尿中",
        "nyouchu",
        "労働衛生",
        "尿中とは？生物学的モニタリング・代謝物",
        "ketsuchu:血中;ketsuchu-noudo:血中濃度;seibutsugaku-monitoring:生物学的モニタリング",
        "尿中有害物質・代謝物濃度の測定です。",
        "尿中濃度と血中濃度の使い分けを理解すること。",
        related_terms_csv="血中;血中濃度;生物学的モニタリング",
    ),
    T(
        263,
        "263-ketsuchu-noudo",
        "血中濃度",
        "ketsuchu-noudo",
        "労働衛生",
        "血中濃度とは？管理濃度・生物学的モニタリング",
        "ketsuchu:血中;kanri-nodo:管理濃度;seibutsugaku-monitoring:生物学的モニタリング",
        "血液中有害物質の濃度指標です。",
        "血中濃度と管理濃度・作業環境測定の違いを整理すること。",
        related_terms_csv="血中;管理濃度;生物学的モニタリング",
    ),
    T(
        264,
        "264-souon",
        "騒音",
        "souon",
        "労働衛生",
        "騒音とは？騒音性難聴・測定・保護具",
        "soonnsei-nacho:騒音性難聴;a-tokusei-soryo-on:A特性騒音レベル;toka-sonn-level:等価騒音レベル",
        "不快・聴力障害を起こす音です。作業環境測定の対象です。",
        "騒音測定と騒音性難聴予防の関係を整理すること。",
        related_terms_csv="騒音性難聴;A特性騒音レベル;等価騒音レベル",
    ),
    T(
        265,
        "265-sagyo-kankyo-kanri-t",
        "作業環境管理",
        "sagyo-kankyo-kanri-t",
        "労働衛生",
        "作業環境管理とは？管理区分・測定・改善",
        "sagyo-kankyo-kanri-kubun:作業環境管理区分;sagyo-kankyo-sokutei:作業環境測定;sagyo-kankyo-kanri-bo:作業環境管理簿",
        "有害物の濃度を管理する一連の制度です。",
        "作業環境管理の流れ（測定→評価→改善）を整理すること。",
        related_terms_csv="作業環境管理区分;作業環境測定;作業環境管理簿",
    ),
    T(
        266,
        "266-bakuro",
        "ばく露",
        "bakuro",
        "労働衛生",
        "ばく露とは？ばく露限界・個人サンプリング",
        "kojin-sampling-ho:個人サンプリング法;passive-sampler:パッシブサンプラー;kanri-nodo:管理濃度",
        "有害物質への接触の程度です。",
        "ばく露の評価方法と作業環境測定の関係を理解すること。",
        related_terms_csv="個人サンプリング法;パッシブサンプラー;管理濃度",
    ),
]


def append_glossary_csv(items: list[dict]) -> int:
    with GLOSSARY_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    existing_terms = {r["term"] for r in rows}
    existing_slugs = {r.get("slug", "") for r in rows}
    added = 0
    for item in items:
        row = csv_row(item)
        if row["term"] in existing_terms or row["slug"] in existing_slugs:
            continue
        rows.append(row)
        existing_terms.add(row["term"])
        existing_slugs.add(row["slug"])
        added += 1
    with GLOSSARY_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return added


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
            "用語35本追加バッチ", "用語50本追加バッチ（第4弾）"
        ).replace("2026-05-19", DATE)
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

    csv_added = append_glossary_csv(NEW_TERMS)
    print(f"done: {created} articles, {csv_added} csv rows, {len(slug_map)} slugs total")


if __name__ == "__main__":
    main()
