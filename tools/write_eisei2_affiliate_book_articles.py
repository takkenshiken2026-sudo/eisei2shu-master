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
            "価格・在庫・版情報は執筆時点（2026-06-12）のAmazon税込参考です。"
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
                    "イラスト中心で三科目の骨格をつかみやすい",
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
        "operator_note": "Amazon tag=ue083093-22。2026-06-12 Amazon販売ページで価格確認（各1,650円税込参考）。",
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
            "価格・在庫は執筆時点（2026-06-12）のAmazon税込参考です。"
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
        "operator_note": "Amazon tag=ue083093-22。労基団連版は年度更新に注意。2026-06-12 価格確認。",
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
        "original_note": "Amazon Associates tag=ue083093-22。比較: 4300121273 / 4297154951 / 4046077956。",
        "user_intent": "独学で使う第二種衛生管理者のテキストを、解説の厚み・演習量・初学者向きで比較して1冊に絞りたい。",
        "action_items": "比較表で3冊の違いを確認する;自分の学習スタイルに合う1冊を選ぶ;二衛マスター過去問で弱点分野を把握する",
        "revision_note": "2026-06-12: テンプレ構成に合わせて本文を全面リライト・Amazon価格再確認",
        "sections": [
            (
                "テキスト選びの3つのポイント",
                "第二種衛生管理者試験のテキスト選びでは、①安全衛生技術試験協会（公式）の出題範囲"
                "（労働生理・労働衛生・関係法令）と科目別合格基準（各40点・足切り）に目次が沿っているか、"
                "②解説量が自分の前提知識に合うか、③章末演習や別冊問題集とセットで使えるかを確認します。\n\n"
                "社会人独学では、通勤で読める分量と週末にまとめて演習できる問題量も判断材料になります。"
                "たとえば6月開始・10月本番なら、第1〜4週でテキスト1章＋科目別10問、第5週から30問本番形式へ移行する計画と"
                "ページ数が見合うかを見てください。1冊に絞れない場合は、テキスト1冊＋過去問専門1冊の2冊構成も有効です。",
            ),
            (
                "おすすめテキスト比較の見方",
                "比較では「図解で骨格を掴む」「解説を厚く読む」「著者の語り口で進める」の3タイプで見ます。"
                "いずれもテキストと演習がセットのALL-in-one型です。"
                "独学初期は理解用1冊に絞り、過去問演習が進んだ段階で問題集を追加する構成が扱いやすいです。"
                "二衛マスターの過去問で科目別得点を記録し、40点未満の科目が出たらテキスト該当章に戻る。"
                "解説の厚みが足りないと感じた冊を基準に選び直すと、買い替えの失敗が減ります。",
            ),
            (
                "1位：スッキリわかるの特徴",
                "2026年度版 スッキリわかる 第2種衛生管理者 テキスト&問題集（TAC出版・1,650円税込参考・448ページ・B5判）は、"
                "イラスト中心で労働生理・労働衛生・関係法令の骨格をつかみやすい定番です。"
                "章末演習でテキストと問題の往復がしやすく、初学者が最初の1冊に選びやすい構成です。"
                "独学ロードマップ（dokugaku-guide）と併用すると、週次の演習量も組み立てやすくなります。\n\n"
                "向いている人：衛生管理者試験が初めてで、図解で論点の地図を作りながら1冊で進めたい人。",
            ),
            (
                "2位：合格教本&問題集の特徴",
                "第2種衛生管理者 合格教本&問題集（技術評論社・1,650円税込参考・496ページ・B5判）は、"
                "教本パートで論点を丁寧に整理し、問題集パートで演習量を確保しやすいバランス型です。"
                "条文・数値の整理をじっくり読みたい人向けで、関係法令の条文対応表も確認しやすい構成です。"
                "テキスト読了後は、おすすめ問題集の記事で演習メイン1冊を追加する流れが定番です。\n\n"
                "向いている人：ある程度基礎があり、解説の厚みと演習量の両方を重視する人。",
            ),
            (
                "3位：村中一英テキストの特徴",
                "改訂3版 この1冊で合格! 村中一英の第2種衛生管理者 テキスト&問題集（KADOKAWA・1,650円税込参考・416ページ・B5判）は、"
                "著者の語り口で暗記→演習のリズムを作りやすい1冊です。"
                "改訂版で最新の出題傾向を反映しており、数値・期限の整理に向いています。"
                "速習から入りたい場合は初学者向け教材の記事も参照してください。\n\n"
                "向いている人：著者の解説トーンで条文・数値を整理したい人。"
                "第二種は30問・3科目なので、一種向け100問教材と混同しないよう表紙表記を確認してください。",
            ),
            (
                "テキストと二衛マスター過去問の併用",
                "テキストで論点を押さえたら、二衛マスターの過去問・一問一答で30問本番形式の演習に移ります。"
                "科目別得点を記録し、足切りライン（各40点）に届いていない科目をテキスト該当章に戻って復習するサイクルが効率的です。"
                "テキストで理解→演習で確認→間違えた論点を用語解説で補強、の順で回してください。"
                "過去問の回し方は past-question-strategy、何年分を優先するかは kakomon-nannennbun で整理できます。",
            ),
            (
                "購入前チェックリスト",
                "購入前に以下を確認してください。\n"
                "・2026年度版（最新版）か\n"
                "・テキストのみ／問題集のみではなくセット版か\n"
                "・Amazon在庫・価格（執筆時点と異なる場合あり）\n"
                "・手元の学習計画（3か月／6か月）に対してページ数・演習量が見合うか\n"
                "・表紙に「第2種」「30問」相当の範囲が明記されているか（第一種100問教材と混同しない）\n"
                "・中古購入の場合は版・書き込みの有無を販売ページの商品説明で確認する",
            ),
        ],
        "faqs": [
            (
                "テキストは1冊だけで足りますか？",
                "ALL-in-one型テキスト1冊＋当サイトの過去問演習で独学は可能です。"
                "演習量が足りないと感じたら、おすすめ問題集の記事で紹介している過去問専門1冊を追加する構成がおすすめです。"
                "30問本番形式で総合180点・各40点を安定して超えられるまで、テキスト該当章への戻りを続けてください。",
            ),
            (
                "第一種向けのテキストを第二種に使えますか？",
                "第一種向け100問教材は範囲が広く、第二種の30問・3科目演習には過剰です。"
                "第二種専用テキストを選び、44問・100問の第一種問題集と混同しないよう注意してください。"
                "一種合格済みでも、第二種の足切り（各40点）確認には30問形式の演習が必要です。",
            ),
            (
                "価格・在庫はどこで確認しますか？",
                "各商品のAmazon販売ページ（本記事の比較表リンク）で、税込価格・在庫・版表記を確認してください。"
                "2026-06-12時点では3冊とも1,650円（税込参考）でしたが、キャンペーンや品切れで変わります。"
                "購入前に目次写真または試し読みで3科目が揃っているかも併せて確認すると安心です。",
            ),
        ],
        "related_links": (
            "dokugaku-guide:独学合格ガイド;"
            "past-question-strategy:過去問の使い方;"
            "kakomon-nannennbun:過去問は何年分;"
            "affiliate-problem-books:おすすめ問題集;"
            "affiliate-beginner-material-set:初学者向け教材セット;"
            "goukaku-kijun:合格基準と足切り;"
            f"{amazon('4300121273')}:2026年度版 スッキリわかる テキスト（Amazon）"
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
            "過去問の使い方と足切り対策も解説。"
        ),
        "lead": (
            "第二種衛生管理者試験では、過去問・予想問題の演習量が得点安定の鍵です。"
            "本記事では2026年度版の問題集3冊を、収録形式・解説量・独学との相性で比較します。"
            "価格は購入前にAmazonで必ずご確認ください。"
        ),
        "priority": "365",
        "original_note": "Amazon tag=ue083093-22。4426616573 / 4415241077 / 4867881015。",
        "user_intent": "第二種衛生管理者の過去問・予想模試付き問題集を比較し、演習のメイン1冊を決めたい。",
        "action_items": "3冊の収録形式を比較する;演習計画に組み込む1冊を選ぶ;足切り分野を過去問で確認する",
        "revision_note": "2026-06-12: Amazon価格を販売ページで再確認して更新",
        "sections": [
            (
                "問題集選びの基準",
                "問題集選びでは、(1)30問本番形式に近いか (2)解説で復習できるか "
                "(3)演習量が計画に見合うかを確認します。"
                "足切り（各科目40点）対策には、科目別に解ける問題集か、解説で弱点科目に戻れるかが重要です。"
                "たとえばテキスト第1周完了後（目安4〜6週）に、週1回30問本番形式をカレンダーに登録し、"
                "問題集1冊をメイン演習に据える計画が定番です。"
                "合格基準（goukaku-kijun）の2条件を演習記録でも毎回確認してください。",
            ),
            (
                "3冊の選び方（タイプ別）",
                "[[affiliate-hub-placeholder]]\n\n"
                "予想模試まで含めて演習量を確保したい人は2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試、"
                "直近の本試験形式を解きたい人は詳解 第2種衛生管理者過去6回問題集 '26年版、"
                "試験実施団体系の形式に慣れたい人は第二種衛生管理者試験問題集 2026年度版が向きます。"
                "いずれも第二種専用（30問・3科目）であることを表紙で確認してから選んでください。"
                "比較表の価格は執筆時点の参考です。",
            ),
            (
                "1位：ユーキャン重要過去問&予想模試",
                "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試（1,760円税込参考・288ページ）は、"
                "重要過去問に加え予想模試が付属し、直前期の総仕上げにも使えます。"
                "テキスト読了後の演習メインにも向き、ユーキャン系列の速習教材との併用もしやすい構成です。"
                "本番2〜4週前に予想模試を1回通しで解き、足切り科目がないか確認する使い方が定番です。"
                "演習後は二衛マスター過去問で同分野を解き直すと定着しやすくなります。",
            ),
            (
                "2位・3位：成美堂過去6回・労基団連",
                "詳解 第2種衛生管理者過去6回問題集 '26年版（成美堂出版・1,540円税込参考・256ページ）は過去6回分を解説付きで収録。"
                "30問・約180分の時間感覚を養うのに適しており、本番の13:30開始に合わせた通し演習にも向きます。\n\n"
                "第二種衛生管理者試験問題集 2026年度版（全国労働基準関係団体連合会・2,200円税込参考・224ページ）は、"
                "試験形式に近い演習が目的の1冊です。他社問題集との使い分けで弱点補強に使えます。"
                "労基団連版は年度更新があるため、購入時は表紙の年度表記を必ず確認してください。",
            ),
            (
                "過去問の回し方（二衛マスターとの併用）",
                "当サイトの過去問で科目別得点を把握したうえで、問題集で「時間を計って30問を解く」練習を行います。"
                "誤答は用語解説で類似論点まで整理し、1週間後に解き直してください。"
                "詳しい手順は past-question-strategy を参照。"
                "210問無料演習と問題集は役割分担が有効で、理解確認は年度別解説付き、本番形式は問題集側に寄せる構成がおすすめです。",
            ),
            (
                "第一種問題集との混同に注意",
                "第一種向けの44問・100問問題集は第二種の30問演習には向きません。"
                "表紙に「第2種」「30問」が明記された2026年度版を選び、"
                "100問・44問の第一種教材と混同しないよう注意してください。"
                "演習記録も3科目・各40点の足切りラインで記録し、総合点だけで判断しない習慣をつけてください。"
                "過去問は何年分を優先するかは kakomon-nannennbun で整理できます。",
            ),
        ],
        "faqs": [
            (
                "過去問だけで合格できますか？",
                "演習量は確保できますが、初めての論点はテキストで理解してから問題集に入る方が効率的です。"
                "おすすめテキストの記事で紹介している1冊と組み合わせる構成を推奨します。"
                "30問通しで総合180点・各40点を安定して超えられるまで、弱点科目の章戻りを続けてください。",
            ),
            (
                "問題集は何冊必要ですか？",
                "メイン1冊＋当サイト過去問で足りる場合が多いです。"
                "予想模試と本試験形式の両方欲しい場合は2冊構成もあります。"
                "3冊を同時に開くより、フェーズごとに1冊に役割を絞ると計画が立てやすくなります。"
                "テキスト未読の論点が多い場合は、先におすすめテキストの記事で1冊を確定してください。",
            ),
            (
                "価格・在庫・最新版はどこで確認しますか？",
                "各商品のAmazon販売ページ（本記事の比較表リンク）で、税込価格・在庫・版表記を確認してください。"
                "2026-06-12時点ではユーキャン1,760円・成美堂1,540円・労基団連2,200円（税込参考）でした。"
                "労基団連版は年度更新があるため、表紙の「2026年度版」表記と試験要項の学習範囲が一致するか購入前に確認してください。",
            ),
        ],
        "related_links": (
            "kakomon-nannennbun:過去問は何年分;"
            "dokugaku-guide:独学合格ガイド;"
            "goukaku-kijun:合格基準と足切り;"
            "affiliate-textbooks-recommend:おすすめテキスト;"
            "affiliate-beginner-material-set:初学者向け教材セット;"
            "past-question-strategy:過去問の使い方;"
            f"{amazon('4426616573')}:ユーキャン重要過去問&予想模試（Amazon）"
        ),
        "key_points": (
            "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試;"
            "詳解 第2種衛生管理者過去6回問題集 '26年版;"
            "第二種衛生管理者試験問題集 2026年度版;"
            "問題集選びの基準;"
            "過去問の回し方"
        ),
    },
}


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
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if not fieldnames:
        raise SystemExit("CSV header missing")

    for row in rows:
        slug = row.get("slug", "")
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
        row["fact_checked_at"] = "2026-06-12"
        row["content_status"] = "published"
        row["related_links"] = cfg["related_links"]
        row["key_points"] = cfg["key_points"]
        for i, (heading, body) in enumerate(cfg["sections"], start=1):
            row[f"section_{i}_heading"] = heading
            body_clean = body.replace("[[affiliate-hub-placeholder]]", "").strip()
            row[f"section_{i}_body"] = body_clean
        for i in range(len(cfg["sections"]) + 1, 8):
            row[f"section_{i}_heading"] = ""
            row[f"section_{i}_body"] = ""
        for i, (q, a) in enumerate(cfg["faqs"], start=1):
            row[f"faq_{i}_question"] = q
            row[f"faq_{i}_answer"] = a
        for i in range(len(cfg["faqs"]) + 1, 4):
            row[f"faq_{i}_question"] = ""
            row[f"faq_{i}_answer"] = ""
        print(f"patched CSV row: {slug}")

    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    write_briefs()
    patch_csv()
    return 0


if __name__ == "__main__":
    sys.exit(main())
