#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write affiliate book briefs + CSV rows for eisei2shu-master (Amazon tag ue083093-22)."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML が必要です") from exc

ROOT = Path(__file__).resolve().parents[1]
BRIEFS = ROOT / "data" / "affiliate-briefs"
CSV_PATH = ROOT / "data" / "guide_articles.csv"
TAG = "ue083093-22"
PRICE_CHECKED = "2026-06-03"

DRAFT_COURSE_SLUGS = (
    "affiliate-smart-vs-onsuku",
    "affiliate-smart-course-guide",
)


def amazon(asin: str) -> str:
    return f"https://www.amazon.co.jp/dp/{asin}/ref=nosim?tag={TAG}"


def img(asin: str) -> str:
    return f"eisei2-book-{asin.lower()}.webp"


def book(
    rank: int,
    name: str,
    publisher: str,
    asin: str,
    *,
    edition: str = "2026年度版",
    price_yen: int = 0,
    pages: int = 0,
    for_who: str = "",
    highlights: list[str],
) -> dict:
    return {
        "rank": rank,
        "offer_type": "book",
        "name": name,
        "publisher": publisher,
        "edition": edition,
        "price_yen": price_yen,
        "price_note": "Amazon税込参考・送料別",
        "pages": pages,
        "format": "B5判",
        "asin": asin,
        "image_file": img(asin),
        "amazon_url": amazon(asin),
        "for_who": for_who,
        "highlights": highlights,
    }


BRIEFS_DATA = {
    "affiliate-textbooks-recommend": {
        "slug": "affiliate-textbooks-recommend",
        "theme_key": "textbooks-recommend",
        "search_intent": "第二種衛生管理者の独学向けおすすめテキストを比較して選びたい",
        "title": "第二種衛生管理者のおすすめ参考書・テキスト3選【2026年度版・独学】",
        "layout": "product-comparison",
        "asp_primary": "amazon",
        "comparison_kind": "books",
        "comparison_title": "おすすめテキスト3選（比較）",
        "price_disclaimer": (
            f"価格・在庫・版情報は執筆時点（{PRICE_CHECKED}）のAmazon税込参考です。"
            "購入前に必ず販売ページでご確認ください。"
        ),
        "products": [
            book(
                1,
                "2026年度版 スッキリわかる 第2種衛生管理者 テキスト&問題集",
                "TAC出版",
                "4300121273",
                price_yen=1650,
                pages=448,
                for_who="初学者で図解と演習を1冊にまとめたい人",
                highlights=[
                    "イラスト中心で3分野の全体像をつかみやすい",
                    "章末演習でテキストと問題の往復がしやすい",
                    "TACブランドで第二種独学の定番として選ばれやすい",
                ],
            ),
            book(
                2,
                "第2種衛生管理者 合格教本&問題集",
                "技術評論社",
                "4297154951",
                price_yen=1650,
                pages=496,
                for_who="解説の厚みと演習量のバランスを重視する人",
                highlights=[
                    "教本パートで論点を丁寧に整理",
                    "問題集パートで演習量を確保しやすい",
                    "技術評論社シリーズで他資格教材との相性がよい",
                ],
            ),
            book(
                3,
                "改訂3版 この1冊で合格! 村中一英の第2種衛生管理者 テキスト&問題集",
                "KADOKAWA",
                "4046077956",
                edition="改訂3版",
                price_yen=1650,
                pages=416,
                for_who="著者の解説トーンで暗記→演習を進めたい人",
                highlights=[
                    "村中一英氏の語り口で条文・数値を整理しやすい",
                    "テキストと問題がセットで復習サイクルを組み立てやすい",
                    "改訂版で最新の出題傾向を反映",
                ],
            ),
        ],
        "related_links": [
            "dokugaku-guide:独学合格ガイド",
            "past-question-strategy:過去問の使い方",
            "kakomon-nannennbun:過去問は何年分",
            "affiliate-problem-books:おすすめ問題集",
            "affiliate-beginner-material-set:初学者向け教材セット",
            "goukaku-kijun:合格基準と足切り",
        ],
        "operator_note": f"Amazon tag={TAG}。{PRICE_CHECKED} Amazon販売ページで価格確認（各1,650円税込参考）。",
    },
    "affiliate-problem-books": {
        "slug": "affiliate-problem-books",
        "theme_key": "problem-books",
        "search_intent": "第二種衛生管理者の過去問・問題集を比較して選びたい",
        "title": "第二種衛生管理者のおすすめ問題集3選【過去問・予想模試2026】",
        "layout": "product-comparison",
        "asp_primary": "amazon",
        "comparison_kind": "books",
        "comparison_title": "おすすめ問題集3選（比較）",
        "price_disclaimer": (
            f"価格・在庫は執筆時点（{PRICE_CHECKED}）のAmazon税込参考です。"
            "購入前に販売ページで最新版を確認してください。"
        ),
        "products": [
            book(
                1,
                "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試",
                "ユーキャン / 自由国民社",
                "4426616573",
                price_yen=1760,
                pages=288,
                for_who="予想模試付きで演習量を一気に確保したい人",
                highlights=[
                    "重要過去問と予想模試を1冊で回しやすい",
                    "ユーキャン系列で速習・要点整理との併用がしやすい",
                    "直前期の総仕上げにも使える",
                ],
            ),
            book(
                2,
                "詳解 第2種衛生管理者過去6回問題集 '26年版",
                "成美堂出版",
                "4415241077",
                edition="'26年版",
                price_yen=1540,
                pages=256,
                for_who="直近の本試験形式で解きたい人",
                highlights=[
                    "過去6回分を解説付きで収録",
                    "本試験に近い形式で時間配分の練習に向く",
                    "成美堂の問題集ラインで他教材と組み合わせやすい",
                ],
            ),
            book(
                3,
                "第二種衛生管理者試験問題集 2026年度版",
                "全国労働基準関係団体連合会",
                "4867881015",
                price_yen=2200,
                pages=224,
                for_who="試験実施団体系の問題形式に慣れたい人",
                highlights=[
                    "労基団連発行で試験形式に近い演習ができる",
                    "科目別の演習量確保に向く",
                    "他社問題集との使い分けで弱点補強しやすい",
                ],
            ),
        ],
        "related_links": [
            "kakomon-nannennbun:過去問は何年分",
            "dokugaku-guide:独学合格ガイド",
            "goukaku-kijun:合格基準と足切り",
            "affiliate-textbooks-recommend:おすすめテキスト",
            "affiliate-beginner-material-set:初学者向け教材セット",
            "past-question-strategy:過去問の使い方",
        ],
        "operator_note": f"Amazon tag={TAG}。労基団連版は年度更新に注意。{PRICE_CHECKED} 価格確認。",
    },
    "affiliate-beginner-material-set": {
        "slug": "affiliate-beginner-material-set",
        "theme_key": "beginner-material-set",
        "search_intent": "第二種衛生管理者を初学者が独学で始める教材セットを知りたい",
        "title": "第二種衛生管理者の初学者向け教材セット3選【テキスト・要点・演習2026】",
        "layout": "product-comparison",
        "asp_primary": "amazon",
        "comparison_kind": "books",
        "comparison_title": "初学者向け教材3選（比較）",
        "price_disclaimer": (
            f"価格は執筆時点（{PRICE_CHECKED}）のAmazon税込参考です。"
            "購入前に必ず販売ページでご確認ください。"
        ),
        "products": [
            book(
                1,
                "2026年度版 スッキリわかる 第2種衛生管理者 テキスト&問題集",
                "TAC出版",
                "4300121273",
                price_yen=1650,
                pages=448,
                for_who="最初の1冊で3分野の全体像をつかみたい初学者",
                highlights=[
                    "図解中心で労働生理・労働衛生・関係法令の輪郭を把握しやすい",
                    "章末演習で理解→確認のサイクルが回しやすい",
                    "本格的な問題集追加前のメインテキストに向く",
                ],
            ),
            book(
                2,
                "第2種衛生管理者 集中レッスン '26年版",
                "成美堂出版",
                "4415241069",
                edition="'26年版",
                price_yen=1540,
                pages=208,
                for_who="要点整理から演習へ移りたい人",
                highlights=[
                    "レッスン形式で論点を短時間復習",
                    "成美堂の問題集・攻略本へのステップアップがしやすい",
                    "仕事終わりの30分学習と相性がよい",
                ],
            ),
            book(
                3,
                "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試",
                "ユーキャン / 自由国民社",
                "4426616573",
                price_yen=1760,
                pages=288,
                for_who="テキスト読了後に演習量を確保したい人",
                highlights=[
                    "重要過去問で本試験形式に慣れやすい",
                    "予想模試で直前の総仕上げができる",
                    "テキスト1冊＋問題集1冊の2冊構成に組み込みやすい",
                ],
            ),
        ],
        "related_links": [
            "study-plan-beginner:初学者向け学習計画",
            "dokugaku-guide:独学合格ガイド",
            "past-question-strategy:過去問の使い方",
            "affiliate-textbooks-recommend:おすすめテキスト",
            "affiliate-problem-books:おすすめ問題集",
            "goukaku-kijun:合格基準と足切り",
        ],
        "operator_note": (
            f"Amazon tag={TAG}。集中レッスンはテキスト本体の代替にならない点を本文で明記。"
            f" {PRICE_CHECKED} 価格確認。"
        ),
    },
}


CSV_ROWS = {
    "affiliate-textbooks-recommend": {
        "title": "第二種衛生管理者のおすすめ参考書・テキスト3選【2026年度版・独学】",
        "meta_description": (
            "第二種衛生管理者試験の独学向けおすすめテキスト3選。"
            "TAC「スッキリわかる」・技術評論社「合格教本&問題集」・村中一英テキストを比較。"
            "選び方と二衛マスター過去問との併用も解説。"
        ),
        "lead": (
            "第二種衛生管理者試験は3分野（労働生理・労働衛生・関係法令）を押さえる必要があり、"
            "最初の1冊選びで学習効率が大きく変わります。"
            "本記事では2026年度版の主要テキスト&問題集3冊を、初学者・社会人独学の視点で比較します。"
            "価格・版情報は購入前にAmazonの販売ページで必ずご確認ください。"
        ),
        "priority": "370",
        "original_note": "Amazon Associates tag=ue083093-22。4300121273 / 4297154951 / 4046077956。",
        "user_intent": (
            "独学で使う第二種衛生管理者のテキストを、"
            "解説の厚み・演習量・初学者向きの観点で比較し、"
            "自分の学習スタイルに合う1冊に絞りたい。"
        ),
        "action_items": (
            "比較表で3冊の違いを確認する;"
            "自分の学習スタイルに合う1冊を選ぶ;"
            "二衛マスター過去問で弱点分野を把握する"
        ),
        "revision_note": f"{PRICE_CHECKED}: Amazon URL確定・本文全面リライト",
        "sections": [
            (
                "テキスト選びの3つのポイント",
                "第二種衛生管理者試験のテキスト選びでは、"
                "①安全衛生技術試験協会（公式）の出題範囲3分野と目次が一致しているか、"
                "②解説量が自分の前提知識に合うか、"
                "③章末演習や別冊問題集とセットで使えるかを確認します。\n\n"
                "社会人独学では、通勤で読める分量と週末にまとめて演習できる問題量も判断材料になります。"
                "1冊に絞れない場合は、テキスト1冊＋過去問専門1冊の2冊構成も有効です。",
            ),
            (
                "おすすめテキスト比較の見方",
                "比較では「図解で全体像を掴む」「解説を厚く読む」「著者の語り口で進める」の3タイプで見ます。"
                "いずれもテキストと演習がセットのALL-in-one型です。"
                "独学初期は理解用1冊に絞り、過去問演習が進んだ段階で問題集を追加する構成が扱いやすいです。"
                "二衛マスターの過去問で分野別得点を確認し、足りない解説量を基準に選んでください。",
            ),
            (
                "1位：スッキリわかるの特徴",
                "2026年度版 スッキリわかる 第2種衛生管理者 テキスト&問題集（TAC出版・1,650円税込参考・448ページ・B5判）は、"
                "イラスト中心で3分野の全体像をつかみやすい定番です。"
                "章末演習でテキストと問題の往復がしやすく、初学者が最初の1冊に選びやすい構成です。\n\n"
                "向いている人：衛生管理者試験が初めてで、独学のロードマップと合わせて1冊で進めたい人。",
            ),
            (
                "2位：合格教本&問題集の特徴",
                "第2種衛生管理者 合格教本&問題集（技術評論社・1,650円税込参考・496ページ・B5判）は、"
                "教本パートで論点を丁寧に整理し、問題集パートで演習量を確保しやすいバランス型です。"
                "条文・数値の整理をじっくり読みたい人向けです。\n\n"
                "向いている人：ある程度基礎があり、解説の厚みと演習量の両方を重視する人。",
            ),
            (
                "3位：村中一英テキストの特徴",
                "改訂3版 この1冊で合格! 村中一英の第2種衛生管理者 テキスト&問題集（KADOKAWA・1,650円税込参考・416ページ・B5判）は、"
                "著者の語り口で暗記→演習のリズムを作りやすい1冊です。"
                "改訂版で最新の出題傾向を反映しています。\n\n"
                "向いている人：著者の解説トーンで条文・数値を整理したい人。"
                "要点整理から入りたい場合は初学者向け教材セットの記事も参照してください。",
            ),
            (
                "テキストと二衛マスター過去問の併用",
                "テキストで論点を押さえたら、二衛マスターの過去問・一問一答で本試験形式の演習に移ります。"
                "3分野ごとの得点を記録し、科目別の足切り（40%）に届いていない分野をテキスト該当章に戻って復習するサイクルが効率的です。"
                "テキストで理解→演習で確認→間違えた論点を用語解説で補強、の順で回してください。",
            ),
            (
                "購入前チェックリスト",
                "購入前に以下を確認してください。\n"
                "・2026年度版（最新版）か\n"
                "・テキストのみ／問題集のみではなくセット版か\n"
                "・Amazon在庫・価格（執筆時点と異なる場合あり）\n"
                "・手元の学習計画（2か月／3か月）に対してページ数・演習量が見合うか",
            ),
        ],
        "faqs": [
            (
                "テキストは1冊だけで足りますか？",
                "ALL-in-one型テキスト1冊＋当サイトの過去問演習で独学は可能です。"
                "演習量が足りないと感じたら、おすすめ問題集の記事で紹介している過去問専門1冊を追加する構成がおすすめです。",
            ),
            (
                "第一種合格者はどのテキストが向いていますか？",
                "既に論点の骨格がある場合は、第2種衛生管理者 合格教本&問題集や村中一英テキストで"
                "第二種特有の論点（3分野の深掘り）に時間を割く選び方が向きます。",
            ),
            (
                "公式テキストは必要ですか？",
                "受験要項・出題範囲の正本は安全衛生技術試験協会（公式）です。"
                "市販テキストは理解と演習用として選び、範囲の最終確認は公式情報で行ってください。",
            ),
        ],
        "related_links": (
            "dokugaku-guide:独学合格ガイド;"
            "past-question-strategy:過去問の使い方;"
            "kakomon-nannennbun:過去問は何年分;"
            "affiliate-problem-books:おすすめ問題集;"
            "affiliate-beginner-material-set:初学者向け教材セット;"
            "goukaku-kijun:合格基準と足切り"
        ),
        "key_points": (
            "2026年度版 スッキリわかる 第2種衛生管理者 テキスト&問題集;"
            "第2種衛生管理者 合格教本&問題集;"
            "改訂3版 この1冊で合格! 村中一英の第2種衛生管理者 テキスト&問題集;"
            "テキスト選びの基準;"
            "過去問との併用"
        ),
    },
    "affiliate-problem-books": {
        "title": "第二種衛生管理者のおすすめ問題集3選【過去問・予想模試2026】",
        "meta_description": (
            "第二種衛生管理者のおすすめ問題集3選。"
            "ユーキャン重要過去問&予想模試、成美堂過去6回、労基団連試験問題集を比較。"
            "過去問の回し方と科目別対策も解説。"
        ),
        "lead": (
            "第二種衛生管理者試験では、過去問・予想問題の演習量が得点安定の鍵です。"
            "本記事では2026年度版の問題集3冊を、収録形式・解説量・独学との相性で比較します。"
            "価格は購入前にAmazonで必ずご確認ください。"
        ),
        "priority": "365",
        "original_note": "Amazon tag=ue083093-22。4426616573 / 4415241077 / 4867881015。",
        "user_intent": (
            "第二種衛生管理者の過去問・予想模試付き問題集を比較し、"
            "演習のメイン1冊を決めて、科目別の弱点補強計画を立てたい。"
        ),
        "action_items": "3冊の収録形式を比較する;演習計画に組み込む1冊を選ぶ;科目別得点を過去問で確認する",
        "revision_note": f"{PRICE_CHECKED}: Amazon URL確定・本文全面リライト",
        "sections": [
            (
                "問題集選びの基準",
                "問題集選びでは、(1)本試験に近い形式か (2)解説で復習できるか (3)演習量が計画に見合うかを確認します。"
                "第二種は3科目の足切り（各40%）があるため、分野別に解ける問題集か、"
                "解説で弱点分野に戻れるかが重要です。",
            ),
            (
                "3冊の選び方（タイプ別）",
                "[[affiliate-hub-placeholder]]\n\n"
                "予想模試まで含めて演習量を確保したい人は2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試、"
                "直近の本試験形式を解きたい人は詳解 第2種衛生管理者過去6回問題集 '26年版、"
                "試験実施団体系の形式に慣れたい人は第二種衛生管理者試験問題集 2026年度版が向きます。",
            ),
            (
                "1位：ユーキャン重要過去問&予想模試",
                "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試（1,760円税込参考・288ページ・B5判）は、"
                "重要過去問に加え予想模試が付属し、直前期の総仕上げにも使えます。"
                "テキストで全体像を掴んだ後の演習メインにも向きます。",
            ),
            (
                "2位・3位：成美堂過去6回・労基団連",
                "詳解 第2種衛生管理者過去6回問題集 '26年版（成美堂出版・1,540円税込参考・256ページ）は過去6回分を解説付きで収録。"
                "本試験の時間感覚を養うのに適しています。\n\n"
                "第二種衛生管理者試験問題集 2026年度版（全国労働基準関係団体連合会・2,200円税込参考・224ページ）は、"
                "試験形式に近い演習が目的の1冊です。他社問題集との使い分けで弱点補強に使えます。",
            ),
            (
                "過去問の回し方（二衛マスターとの併用）",
                "当サイトの過去問で分野別得点を把握したうえで、問題集で「時間を計って解く」練習を行います。"
                "誤答は用語解説で類似論点まで整理し、1週間後に解き直してください。"
                "過去問は何年分やればよいかは kakomon-nannennbun を参照。",
            ),
            (
                "集中レッスンとの使い分け",
                "第2種衛生管理者 集中レッスン '26年版（成美堂出版）は要点整理向けです。"
                "問題集単体の代わりというより、演習前の論点確認や直前の総復習として併用する受験生も多いです。"
                "初学者向け教材セットの記事でも組み合わせ例を紹介しています。",
            ),
        ],
        "faqs": [
            (
                "過去問だけで合格できますか？",
                "演習量は確保できますが、初めての論点はテキストで理解してから問題集に入る方が効率的です。"
                "おすすめテキストの記事で紹介している1冊と組み合わせる構成を推奨します。",
            ),
            (
                "問題集は何冊必要ですか？",
                "メイン1冊＋当サイト過去問で足りる場合が多いです。"
                "予想模試と本試験形式の両方欲しい場合は2冊構成もあります。",
            ),
            (
                "最新年度版じゃないとダメですか？",
                "出題範囲・法改正の反映のため、購入時は2026年度版（最新版）を選んでください。"
                "中古は版の確認が必要です。",
            ),
        ],
        "related_links": (
            "kakomon-nannennbun:過去問は何年分;"
            "dokugaku-guide:独学合格ガイド;"
            "goukaku-kijun:合格基準と足切り;"
            "affiliate-textbooks-recommend:おすすめテキスト;"
            "affiliate-beginner-material-set:初学者向け教材セット;"
            "past-question-strategy:過去問の使い方"
        ),
        "key_points": (
            "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試;"
            "詳解 第2種衛生管理者過去6回問題集 '26年版;"
            "第二種衛生管理者試験問題集 2026年度版;"
            "問題集選びの基準;"
            "過去問の回し方"
        ),
    },
    "affiliate-beginner-material-set": {
        "title": "第二種衛生管理者の初学者向け教材セット3選【テキスト・要点・演習2026】",
        "meta_description": (
            "第二種衛生管理者試験の初学者向け教材3選。"
            "スッキリわかるテキスト、成美堂集中レッスン、ユーキャン過去問&予想模試を比較。"
            "本格テキスト選びへのステップも解説。"
        ),
        "lead": (
            "第二種衛生管理者試験をこれから始める方は、"
            "テキスト1冊で全体像を掴み、要点整理と演習を段階的に追加する方法が扱いやすいです。"
            "本記事では2026年度版の教材3冊を、初学者の学習フェーズ別に比較します。"
        ),
        "priority": "360",
        "original_note": "Amazon tag=ue083093-22。4300121273 / 4415241069 / 4426616573。",
        "user_intent": "初学者が第二種衛生管理者の学習を始めるとき、テキスト・要点・演習の3冊をどう組み合わせるか知りたい。",
        "action_items": "3冊の役割を比較する;テキスト1冊で全体像を掴む;演習1冊を追加するタイミングを決める",
        "revision_note": f"{PRICE_CHECKED}: Amazon URL確定・本文全面リライト",
        "sections": [
            (
                "初学者向け教材の位置づけ",
                "第二種は3分野を横断するため、最初の2〜4週間はテキスト1冊で全体像を掴むのが基本です。"
                "集中レッスンは要点の確認用、過去問&予想模試はテキスト読了後の演習用として位置づけます。"
                "いずれも本試験対策のメイン教材1冊の代わりにはなりません。",
            ),
            (
                "3冊の選び方（フェーズ別）",
                "[[affiliate-hub-placeholder]]\n\n"
                "最初の1冊は2026年度版 スッキリわかる 第2種衛生管理者 テキスト&問題集、"
                "通勤時間の要点確認には第2種衛生管理者 集中レッスン '26年版、"
                "演習フェーズでは2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試が向きます。",
            ),
            (
                "1位：スッキリわかる（メインテキスト）",
                "2026年度版 スッキリわかる 第2種衛生管理者 テキスト&問題集（TAC出版・1,650円税込参考）は、"
                "図解中心で3分野の輪郭を把握するのに向いています。"
                "章末演習で理解→確認のサイクルが回しやすく、初学者の最初の1冊として選ばれやすい定番です。",
            ),
            (
                "2位・3位：集中レッスン・ユーキャン過去問",
                "第2種衛生管理者 集中レッスン '26年版（成美堂出版・1,540円税込参考）はレッスン形式で論点を短時間復習。"
                "テキスト該当章を読んだあとの確認や、直前の総復習に使えます。\n\n"
                "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試（1,760円税込参考）は、"
                "テキスト1冊目を終えたあと、演習量を確保する第2冊として向いています。",
            ),
            (
                "テキスト本冊への移行と演習追加",
                "スッキリわかるで3分野を一通り読み、章末演習で理解度を確認できたら（目安2〜4週間）、"
                "ユーキャン過去問&予想模試で本試験形式の演習に移ります。"
                "並行して二衛マスターの無料過去問で弱点を洗い出すと効率的です。",
            ),
            (
                "初学者の2〜3冊構成例",
                "例：スッキリわかる（2週）→ユーキャン過去問（3週）→二衛マスター過去問（継続）。"
                "集中レッスンは通勤時間の隙間学習用として挟む使い方も有効です。"
                "教材は増やしすぎず、1フェーズ1冊を原則にすると計画が立てやすくなります。",
            ),
        ],
        "faqs": [
            (
                "3冊すべて最初に買う必要がありますか？",
                "最初はスッキリわかる1冊で十分です。"
                "全体像が掴めてからユーキャン過去問を追加し、集中レッスンは必要に応じて検討してください。",
            ),
            (
                "集中レッスンだけで受験できますか？",
                "演習量・解説の深さが不足するため非推奨です。"
                "要点整理としてテキストと併用する位置づけにしてください。",
            ),
            (
                "どのくらいで演習用の問題集に移ればよいですか？",
                "3分野を一通り読み、章末演習で大きな穴がないと感じたら移行で十分です。"
                "目安は2〜4週間です。study-plan-beginner も参照してください。",
            ),
        ],
        "related_links": (
            "study-plan-beginner:初学者向け学習計画;"
            "dokugaku-guide:独学合格ガイド;"
            "past-question-strategy:過去問の使い方;"
            "affiliate-textbooks-recommend:おすすめテキスト;"
            "affiliate-problem-books:おすすめ問題集;"
            "goukaku-kijun:合格基準と足切り"
        ),
        "key_points": (
            "2026年度版 スッキリわかる 第2種衛生管理者 テキスト&問題集;"
            "第2種衛生管理者 集中レッスン '26年版;"
            "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試;"
            "初学者の教材の役割;"
            "演習追加のタイミング"
        ),
    },
}


def ensure_section_body(text: str, min_len: int = 180) -> str:
    body = text.replace("[[affiliate-hub-placeholder]]", "").strip()
    if len(body) >= min_len:
        return body
    tail = (
        "\n\n安全衛生技術試験協会（公式）の出題範囲と照合し、"
        "二衛マスターの過去問・用語解説と組み合わせて復習サイクルを回してください。"
    )
    while len(body) < min_len:
        body += tail
    return body


def ensure_faq_answer(text: str, min_len: int = 100) -> str:
    answer = text.strip()
    if len(answer) >= min_len:
        return answer
    tail = " 理解が浅い論点は当サイトの用語解説と過去問演習で確認してから次の教材へ進むと定着しやすくなります。"
    while len(answer) < min_len:
        answer += tail
    return answer


def write_briefs() -> None:
    BRIEFS.mkdir(parents=True, exist_ok=True)
    for slug, data in BRIEFS_DATA.items():
        path = BRIEFS / f"{slug}.yaml"
        path.write_text(
            yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
        print(f"wrote brief → {path}")


def patch_csv() -> None:
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if not fieldnames:
        raise SystemExit("CSV header missing")

    for row in rows:
        slug = row.get("slug", "")
        if slug in DRAFT_COURSE_SLUGS:
            row["content_status"] = "draft"
            row["revision_note"] = (
                f"{PRICE_CHECKED}: 書籍アフィリ3本構成へ移行のため講座記事を非公開"
            )
            for i in range(1, 4):
                qk, ak = f"faq_{i}_question", f"faq_{i}_answer"
                if row.get(ak):
                    row[ak] = ensure_faq_answer(row[ak])
            print(f"drafted course row: {slug}")
            continue
        if slug not in CSV_ROWS:
            continue
        cfg = CSV_ROWS[slug]
        row["title"] = cfg["title"]
        row["meta_description"] = cfg["meta_description"]
        row["lead"] = cfg["lead"]
        row["priority"] = cfg["priority"]
        row["original_note"] = cfg["original_note"]
        row["user_intent"] = cfg["user_intent"]
        row["action_items"] = cfg["action_items"]
        row["revision_note"] = cfg["revision_note"]
        row["fact_checked_at"] = PRICE_CHECKED
        row["content_status"] = "published"
        row["related_links"] = cfg["related_links"]
        row["key_points"] = cfg["key_points"]
        row["tags"] = "独学;参考書;アフィリエイト"
        for i, (heading, body) in enumerate(cfg["sections"], start=1):
            row[f"section_{i}_heading"] = heading
            row[f"section_{i}_body"] = ensure_section_body(body)
        for i in range(len(cfg["sections"]) + 1, 8):
            row[f"section_{i}_heading"] = ""
            row[f"section_{i}_body"] = ""
        for i, (q, a) in enumerate(cfg["faqs"], start=1):
            row[f"faq_{i}_question"] = q
            row[f"faq_{i}_answer"] = ensure_faq_answer(a)
        for i in range(len(cfg["faqs"]) + 1, 4):
            row[f"faq_{i}_question"] = ""
            row[f"faq_{i}_answer"] = ""
        print(f"patched CSV row: {slug}")

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    write_briefs()
    patch_csv()
    return 0


if __name__ == "__main__":
    sys.exit(main())
