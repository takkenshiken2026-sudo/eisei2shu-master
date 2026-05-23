"""労働生理の手作り用語データ（import 専用）。"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any


_HERE = Path(__file__).resolve().parent
_COMMON = _HERE / "common.py"
_spec = importlib.util.spec_from_file_location("handmade_common", _COMMON)
_common = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_common)
I = _common.I


CATEGORY = "労働生理"


HEAT = {"不感蒸泄", "発汗", "熱けいれん", "熱射病", "日射病", "体温調節", "代謝率"}
NEURO = {
    "中枢神経系",
    "大脳",
    "副交感神経",
    "自律神経",
    "交感神経",
    "末梢神経系",
    "神経核",
    "神経節",
    "小脳",
    "体性神経",
}
VIBRATION = {"白ろう", "レイノー現象", "振動障害", "手先振動", "全身振動"}
NOISE = {"聴力レベル", "騒音性難聴", "騒音障害"}
INFECTION = {"病原体", "キャリア", "不顕性感染", "飛沫感染", "感染症", "空気感染", "日和見感染", "接触感染"}
DUST = {"粉じん", "石綿粉じん", "じん肺", "石綿", "シリカ"}
RADIATION = {"電離放射線", "被ばく", "実効線量", "等価線量・吸収線量"}
PRESSURE_OXYGEN = {"減圧症", "高気圧作業", "二酸化炭素", "酸素欠乏症"}


TOPICS: dict[str, dict[str, str]] = {
    "熱中症・体温調節": {
        "focus": "暑熱環境での体温上昇、発汗、水分・塩分喪失",
        "confusion": "日射病・熱けいれん・熱射病を同じ重症度として扱う選択肢",
        "scene": "高温多湿作業、屋外作業、休憩不足の場面",
        "symptom": "めまい、けいれん、意識障害などを重症度で分ける",
        "cause": "産熱が放熱を上回り、発汗・皮膚血流による調節が追いつかない",
        "route": "気温だけでなく湿度、輻射熱、代謝率、水分・塩分補給で評価する",
        "decision": "症状名だけでなく、汗・塩分・意識状態から病態を選ぶ",
        "physiology": "視床下部を中心に発汗、皮膚血管拡張、震えで体温を調節する",
        "comparison": "暑熱時は放熱促進、寒冷時は血管収縮と産熱亢進",
        "timeframe": "作業中から短時間で悪化し、休憩・補給・冷却が遅れると重症化する",
        "prevention": "WBGT、作業休止、水分・塩分補給、暑熱順化を組み合わせる",
    },
    "神経": {
        "focus": "中枢・末梢、自律・体性、交感・副交感の分類",
        "confusion": "神経核と神経節、中枢神経系と末梢神経系を入れ替える選択肢",
        "scene": "感覚・運動・内臓調節をどの神経系が担うかを問う場面",
        "symptom": "運動、感覚、自律機能のどこに影響が出るかで整理する",
        "cause": "脳・脊髄・末梢神経の役割分担と伝達経路の違い",
        "route": "随意運動は体性神経、内臓調節は自律神経として区別する",
        "decision": "部位名と機能名を対応させ、逆の説明を誤りとして見抜く",
        "physiology": "神経細胞の興奮と伝達により、感覚入力と運動・自律反応が調整される",
        "comparison": "交感神経は活動時、副交感神経は休息時に優位になりやすい",
        "timeframe": "反射や自律反応は短時間で現れ、器質的障害は持続しやすい",
        "prevention": "有害物質の神経毒性、振動、騒音などの作用部位と結びつけて学ぶ",
    },
    "振動": {
        "focus": "手腕振動と全身振動、末梢循環障害、神経障害",
        "confusion": "振動障害を騒音障害や石綿障害として扱う選択肢",
        "scene": "振動工具、チェーンソー、車両運転などのばく露場面",
        "symptom": "白ろう、しびれ、冷感、握力低下などを確認する",
        "cause": "反復する機械的振動が血管攣縮や末梢神経障害を起こす",
        "route": "手先振動は手腕、全身振動は腰背部や全身負荷として整理する",
        "decision": "白ろう・レイノー現象が出たら振動ばく露との関係を疑う",
        "physiology": "寒冷刺激や振動により末梢血管が収縮し、指の色調変化が起こる",
        "comparison": "手腕振動は指先症状、全身振動は腰痛・疲労などが中心",
        "timeframe": "短時間の不快感ではなく、反復ばく露で慢性化しやすい",
        "prevention": "工具管理、作業時間管理、防振手袋、保温を組み合わせる",
    },
    "騒音": {
        "focus": "聴力レベル、騒音性難聴、騒音ばく露の管理",
        "confusion": "聴力レベルと騒音レベルを同じ指標として扱う選択肢",
        "scene": "騒音作業場、聴力検査、耳栓・耳覆いの選定場面",
        "symptom": "高音域からの聴力低下、耳鳴り、会話の聞き取りにくさを整理する",
        "cause": "内耳の有毛細胞が長時間の騒音で障害される",
        "route": "音源対策、伝ぱ経路対策、保護具の順に管理を考える",
        "decision": "一時的な耳鳴りだけでなく、感音性難聴としての特徴を見る",
        "physiology": "外耳・中耳で伝えた振動を内耳が神経信号に変換する",
        "comparison": "騒音レベルは環境、聴力レベルは人側の聞こえの指標",
        "timeframe": "反復ばく露で進行し、回復しにくい難聴につながる",
        "prevention": "測定、設備改善、作業時間管理、聴力保護具、健診を組み合わせる",
    },
    "感染": {
        "focus": "病原体、感染経路、発症の有無、抵抗力低下",
        "confusion": "空気感染・飛沫感染・接触感染を粒子径や経路なしに混同する選択肢",
        "scene": "咳・くしゃみ、手指・器具、換気不足の職場場面",
        "symptom": "発熱や呼吸器症状だけでなく、無症状の保菌・感染も区別する",
        "cause": "病原体、感染源、感染経路、宿主感受性がそろうと成立する",
        "route": "空気、飛沫、接触のどの経路かを具体例で判断する",
        "decision": "症状がない感染と抵抗力低下時の発症を分けて読む",
        "physiology": "免疫反応により発症を抑えることがあるが、保菌状態でも伝播しうる",
        "comparison": "不顕性感染は無症状、日和見感染は抵抗力低下時の発症が軸",
        "timeframe": "潜伏、発症、回復、保菌の段階で感染対策が変わる",
        "prevention": "手指衛生、換気、標準予防策、体調不良時の就業配慮を押さえる",
    },
    "粉じん": {
        "focus": "粉じんばく露、じん肺、石綿・シリカの慢性影響",
        "confusion": "粉じんを石綿だけ、または急性毒性だけとして扱う選択肢",
        "scene": "研磨、切断、解体、鉱物性粉じんを扱う作業場",
        "symptom": "せき、息切れ、肺線維化など慢性呼吸器障害を整理する",
        "cause": "吸入された微細粒子が肺に沈着し、炎症や線維化を起こす",
        "route": "吸入ばく露が中心で、粒径と発生源対策が重要になる",
        "decision": "急性症状より、長期ばく露と健診・管理区分の流れで読む",
        "physiology": "肺胞に沈着した粒子は除去されにくく、慢性的な反応につながる",
        "comparison": "一般粉じん、石綿、シリカでは疾患名と規制の厳しさが異なる",
        "timeframe": "年月単位の長期ばく露で問題化し、潜伏期間が長いものがある",
        "prevention": "湿潤化、局所排気、呼吸用保護具、特殊健診を組み合わせる",
    },
    "放射線": {
        "focus": "線量指標、被ばく管理、電離作用による健康影響",
        "confusion": "吸収線量・等価線量・実効線量を同じ意味として扱う選択肢",
        "scene": "放射線業務、線量測定、管理区域での作業場面",
        "symptom": "急性障害と晩発影響を分け、線量管理の語と結びつける",
        "cause": "電離作用により細胞やDNAが損傷を受ける",
        "route": "外部被ばくと内部被ばくを分け、測定値の意味を確認する",
        "decision": "どの線量が何を表すかを、単位名だけでなく目的で判断する",
        "physiology": "細胞分裂の盛んな組織ほど影響を受けやすい",
        "comparison": "吸収線量はエネルギー、等価線量は線質、実効線量は組織影響を考慮する",
        "timeframe": "高線量では急性影響、低線量の蓄積では確率的影響が論点になる",
        "prevention": "時間短縮、距離確保、遮へい、個人線量管理を基本にする",
    },
    "高気圧・酸素欠乏": {
        "focus": "酸素濃度、換気、減圧、溶解ガスの変化",
        "confusion": "高気圧作業は加圧だけ、酸素欠乏は二酸化炭素中毒だけとする選択肢",
        "scene": "潜水、シールド工事、タンク・マンホールなどの閉鎖空間",
        "symptom": "頭痛、めまい、意識障害、関節痛などを原因別に整理する",
        "cause": "酸素不足、有毒ガス、急激な減圧による気泡形成が問題になる",
        "route": "空気環境の測定、換気、呼吸用保護具、減圧手順で管理する",
        "decision": "酸素欠乏、有毒ガス、減圧症を同じ症状名だけで混同しない",
        "physiology": "酸素供給が低下すると脳が早く影響を受け、減圧では溶解ガスが気泡化する",
        "comparison": "酸素欠乏は酸素不足、減圧症は圧変化、有毒ガスは毒作用が中心",
        "timeframe": "閉鎖空間では短時間で重症化し、減圧症は浮上・減圧後に出ることがある",
        "prevention": "事前測定、換気、監視、救出体制、段階的減圧を押さえる",
    },
    "化学物質毒性": {
        "focus": "急性・慢性毒性、発がん性、感作性、標的臓器",
        "confusion": "急性毒性・慢性毒性・発がん性を同義として扱う選択肢",
        "scene": "有機溶剤、金属、刺激性ガス、農薬などを扱う作業場",
        "symptom": "刺激症状、中枢神経症状、呼吸器障害、造血器障害などを物質別に見る",
        "cause": "吸入、経皮、経口で体内に入り、代謝・蓄積・排泄の差が影響する",
        "route": "ばく露経路と標的臓器をセットで確認する",
        "decision": "物質名から代表的な健康影響と管理の入口を選ぶ",
        "physiology": "体内に入った物質は血液で運ばれ、肝臓で代謝されるものや脂肪に蓄積するものがある",
        "comparison": "急性は短期ばく露、慢性は長期ばく露、感作は少量再ばく露で反応する",
        "timeframe": "すぐ出る刺激・中毒と、長期に問題化する発がん性・蓄積性を分ける",
        "prevention": "SDS、表示、局所排気、保護具、特殊健診、作業主任者を関連づける",
    },
}


def _topic_for(term: str) -> str:
    if term in HEAT:
        return "熱中症・体温調節"
    if term in NEURO:
        return "神経"
    if term in VIBRATION:
        return "振動"
    if term in NOISE:
        return "騒音"
    if term in INFECTION:
        return "感染"
    if term in DUST:
        return "粉じん"
    if term in RADIATION:
        return "放射線"
    if term in PRESSURE_OXYGEN:
        return "高気圧・酸素欠乏"
    return "化学物質毒性"


def _clean_short_def(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"出題では.*$", "", text).strip()
    text = re.sub(r"^(.+?)は衛生管理者試験の労働生理で扱う用語です。\1は衛生管理者試験の労働生理で扱う用語です。", "", text)
    text = re.sub(r"^(.+?)は衛生管理者試験の労働生理で扱う用語です。", "", text)
    return text.rstrip("。") + "。"


def _pitfall(text: str, topic: str) -> str:
    match = re.search(r"出題では「([^」]+)」", text)
    if match:
        return match.group(1)
    return TOPICS[topic]["confusion"]


def _tables(term: str, topic: str) -> list[tuple[str, list[list[str]]]]:
    t = TOPICS[topic]
    return [
        (
            "症状・疾患の見分け",
            [
                ["観点", term, "混同しやすい判断"],
                ["主な症状・影響", t["symptom"], t["confusion"]],
                ["原因・経路", t["cause"], t["route"]],
                ["試験での判定", t["decision"], "用語名だけでなく、原因・経路・時間軸まで読む"],
            ],
        ),
        (
            "生理・ばく露の比較",
            [
                ["比較軸", term, "対比する考え方"],
                ["体の反応", t["physiology"], t["comparison"]],
                ["時間軸", t["timeframe"], "短期の症状と長期の健康影響を分ける"],
                ["管理の入口", t["prevention"], "症状が出てからではなく、ばく露前の管理を重視する"],
            ],
        ),
    ]


def _make_item(raw: dict[str, Any]) -> dict:
    term = raw["term"]
    slug = raw["slug"]
    topic = _topic_for(term)
    t = TOPICS[topic]
    brief = _clean_short_def(raw["short_def"])
    pitfall = _pitfall(raw["short_def"], topic)
    tips = [
        f"{term}は{brief} {t['focus']}と結びつけて押さえる。",
        f"誤り肢は「{pitfall}」の形で出やすいので、{t['confusion']}に注意する。",
        f"{t['scene']}を想定し、{term}を症状・原因・予防の順に判断する。",
    ]
    csv_desc = (
        f"{term}（労働生理）は、{brief} "
        f"{topic}の論点として、{t['focus']}を症状・疾患、体の反応、予防策の表で整理します。"
    )
    return I(
        term=term,
        slug=slug,
        category=CATEGORY,
        title=f"{term}とは？労働生理での意味・症状・試験ポイント",
        csv_desc=csv_desc,
        tips=tips,
        tables=_tables(term, topic),
    )


_RAW_TERMS: list[dict[str, Any]] = json.loads(
    (_HERE / "terms_limit.json").read_text(encoding="utf-8")
)
if len(_RAW_TERMS) != 66:
    raise ValueError(f"terms_limit.json must contain 66 terms, got {len(_RAW_TERMS)}")

HANDMADE_LIMIT: list[dict] = [_make_item(raw) for raw in _RAW_TERMS]

_csv_descs = [item["csv_desc"] for item in HANDMADE_LIMIT]
if len(_csv_descs) != len(set(_csv_descs)):
    raise ValueError("HANDMADE_LIMIT csv_desc must be unique")
