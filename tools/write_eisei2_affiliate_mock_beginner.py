#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write affiliate mock-exam + beginner-set briefs + CSV rows for eisei2shu-master."""

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
OFFICIAL = "安全衛生技術試験協会（公式）"


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
    "affiliate-mock-exam-materials": {
        "slug": "affiliate-mock-exam-materials",
        "theme_key": "mock-exam-materials",
        "search_intent": "第二種衛生管理者試験の模試・予想問題を比較して選びたい",
        "title": "第二種衛生管理者試験の模試・予想問題3選【30問本番形式2026】",
        "layout": "product-comparison",
        "asp_primary": "amazon",
        "comparison_kind": "books",
        "comparison_title": "模試・予想問題3選（比較）",
        "price_disclaimer": (
            "価格は執筆時点（2026-06-15）のAmazon税込参考です。"
            "試験形式は要項で必ず確認してください。"
        ),
        "products": [
            book(
                1,
                "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試",
                "ユーキャン / 自由国民社",
                "4426616573",
                price_yen=1760,
                pages=288,
                for_who="予想模試付きで直前の総仕上げをしたい人",
                highlights=[
                    "重要過去問と予想模試を1冊で30問本番形式に慣れやすい",
                    "直前期の模試回数を確保しやすい",
                    "ユーキャン系列で要点整理教材との併用がしやすい",
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
                for_who="直近の本試験形式で模試を回したい人",
                highlights=[
                    "過去6回分を解説付きで収録",
                    "13:30開始·180分の本番形式演習に向く",
                    "成美堂集中レッスンからのステップアップがしやすい",
                ],
            ),
            book(
                3,
                "第二種衛生管理者試験問題集 2026年度版",
                "全国労働基準関係団体連合会",
                "4867881015",
                price_yen=2200,
                pages=224,
                for_who="試験実施団体系の形式で模試を受けたい人",
                highlights=[
                    "労基団連発行で本試験形式に近い演習ができる",
                    "科目別の模試分析に向く",
                    "他社問題集との使い分けで弱点補強しやすい",
                ],
            ),
        ],
        "related_links": [
            "mock-exam-how-to:模試の活用法",
            "timed-practice:時間を計った演習",
            "past-question-strategy:過去問の使い方",
            "affiliate-problem-books:おすすめ問題集",
            "affiliate-textbooks-recommend:おすすめテキスト",
            "goukaku-kijun:合格基準と足切り",
        ],
        "operator_note": f"Amazon tag={TAG}。4426616573 / 4415241077 / 4867881015。2026-06-15 価格確認。",
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
            "価格は執筆時点（2026-06-15）のAmazon税込参考です。"
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
                for_who="最初の1冊で三科目の骨格をつかみたい初学者",
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
            " 2026-06-15 価格確認。"
        ),
    },
}


CSV_ROWS = {
    "affiliate-mock-exam-materials": {
        "title": "第二種衛生管理者試験の模試・予想問題3選【30問本番形式2026】",
        "meta_description": (
            "第二種衛生管理者試験の模試・予想問題3選。"
            "ユーキャン予想模試·成美堂過去6回·労基団連問題集を比較。"
            "30問·180分本番形式の模試回数と使い分けを解説。"
        ),
        "lead": (
            "第二種衛生管理者試験は30問·約3時間（180分）·3科目×各10問で、"
            "総合180点かつ各科目40点以上（足切り）が合格基準です（要項で再確認）。"
            "本番形式の模試は、テキスト第1周と問題集演習のあとに入れるのが定番です。"
            "本記事では2026年度版の模試·予想問題付き教材3冊を比較します。"
            "価格は購入前にAmazonで必ずご確認ください。"
        ),
        "priority": "360",
        "original_note": f"Amazon tag={TAG}。4426616573 / 4415241077 / 4867881015。",
        "user_intent": "第二種の30問本番形式模試に使う市販教材を比較して1冊に絞りたい。",
        "action_items": (
            "模試はテキスト第1周後から入れる;"
            "3冊の模試用途差を比較表で確認する;"
            "13:30開始·180分で30問通しを月1〜2回入れる;"
            "科目別40点未満は24時間以内に解き直す;"
            "affiliate-problem-booksで演習のメイン1冊を先に決める"
        ),
        "revision_note": "2026-06-15: Amazon比較記事として全面リライト·published",
        "sections": [
            (
                "模試・予想問題の位置づけ",
                "第二種の模試は、テキストで論点を押さえたあと、"
                "30問·180分·3科目の本番形式で得点を測る演習です。"
                f"試験形式·合格基準は{OFFICIAL}の要項で確認してください。"
                "一種向け100問教材は第二種の30問演習には過剰なので、"
                "表紙に「第2種」「30問」相当の範囲が明記されているかを購入前に確認します。"
                "たとえば8月から日曜13:30·30問·180分を月2回入れ、"
                "9月から予想模試を追加する計画が定番です。",
            ),
            (
                "3冊の選び方（模試用途別）",
                "予想模試まで含めて直前期の総仕上げをしたい人は"
                "「ユーキャン 重要過去問&予想模試」、"
                "直近の本試験形式で模試を回したい人は「成美堂 過去6回問題集」、"
                "試験実施団体系の形式に慣れたい人は「労基団連 試験問題集」が向きます。"
                "いずれも第二種専用（30問·3科目）かを表紙で確認し、"
                "すでに使っているテキスト·問題集と出版社系列を揃えると復習効率が上がります。"
                "迷った場合は、おすすめ問題集の記事で決めた1冊を模試のメインに据えるのが失敗しにくい選び方です。",
            ),
            (
                "1位：ユーキャン予想模試付きの特徴",
                "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試"
                "（ユーキャン / 自由国民社·1,760円税込参考·288ページ·B5判）は、"
                "予想模試付きで直前期の模試回数を確保したい人向けです。"
                "重要過去問で本試験形式に慣れたあと、予想模試を13:30開始·180分で受ける流れが組みやすい1冊です。"
                "科目別得点を記録し、40点未満科目はテキスト該当章に戻って復習するサイクルが定着しやすい構成です。\n\n"
                "向いている人：直前1〜2ヶ月で予想模試を2回以上入れたい人。",
            ),
            (
                "2位：成美堂過去6回の特徴",
                "詳解 第2種衛生管理者過去6回問題集 '26年版"
                "（成美堂出版·1,540円税込参考·256ページ·B5判）は、"
                "直近6回分を解説付きで収録し、本試験に近い形式で模試を回したい人向けです。"
                "成美堂集中レッスンからのステップアップとして、"
                "過去回を1回ずつ30問·180分で受ける計画が立てやすい1冊です。"
                "mock-exam-how-to記事の模試スケジュールと併用すると、"
                "8月·9月·10月の3回模試日程に割り当てやすくなります。\n\n"
                "向いている人：直近の本試験形式で模試を重ねたい人。",
            ),
            (
                "3位：労基団連問題集の特徴",
                "第二種衛生管理者試験問題集 2026年度版"
                "（全国労働基準関係団体連合会·2,200円税込参考·224ページ·B5判）は、"
                "試験実施団体系の形式に慣れたい人向けです。"
                "科目別の模試分析に向き、他社問題集との使い分けで弱点補強しやすい構成です。"
                "ユーキャンや成美堂で演習を進めたあと、"
                "別形式の模試として1回入れると出題の偏りに気づきやすくなります。"
                "年度更新に注意し、購入前に版表記を販売ページで確認してください。\n\n"
                "向いている人：試験形式のバリエーションを確保したい人。",
            ),
            (
                "模試スケジュールの具体例（6月開始）",
                "例：6〜8月はテキスト第1周→9月から問題集で週30問→"
                "8/3（日）·9/7（日）·10/5（日）に13:30開始·30問·180分の模試を入れる。"
                "各模試後は科目別得点と時間切れ有無を記録し、"
                "40点未満科目の誤答を24時間以内に解き直します。"
                "時間計測はtimed-practice記事、配分はtime-limit-strategy記事で先に整理すると"
                "模試結果の読み取りがぶれにくくなります。",
            ),
            (
                "購入前チェックリスト",
                "購入前に以下を確認してください。\n"
                "・2026年度版（最新版）か\n"
                "・第二種衛生管理者試験専用か（第一種100問教材と混同しない）\n"
                "・30問·3科目の本番形式で使えるか\n"
                "・模試をテキスト第1周前に入れない計画か\n"
                "・Amazon在庫·価格（執筆時点と異なる場合あり）\n"
                "・購入直前にAmazon販売ページで版表記·在庫状況を再確認してください。"
                "演習のメイン1冊はaffiliate-problem-booksで先に決め、"
                "模試用途が重複しないよう比較表で役割を整理してから購入してください。",
            ),
        ],
        "faqs": [
            (
                "模試はいつから始めればよいですか？",
                "テキスト第1周完了後（目安4〜6週）から、科目別10問·60分を挟み、"
                "第9週頃から30問·180分の本番形式へ移行するのが定番です。"
                "いきなり模試から始めると論点不足で得点が読めず、"
                "復習の優先順位がつけにくくなります。",
            ),
            (
                "問題集記事と同じASINを買う必要がありますか？",
                "同じASINでも、本記事は模試·予想問題の使い方に特化して説明しています。"
                "問題集記事で1冊を決めたうえで、模試回数と日程を本記事で整理してください。"
                "重複購入を避けるため、手元の問題集がユーキャンなら成美堂過去6回を"
                "別形式模試として使う構成も有効です。",
            ),
            (
                "第一種向けの模試教材は使えますか？",
                "第二種は30問·3科目なので、第一種向け100問教材は範囲が広く演習に過剰です。"
                "表紙に「第2種」「30問」相当の範囲が明記されているかを必ず確認し、"
                "一種合格済みでも30問形式の模試で足切り（各40点）を確認してください。",
            ),
        ],
        "related_links": (
            "mock-exam-how-to:模試の活用法;"
            "timed-practice:時間を計った演習;"
            "time-limit-strategy:時間配分の戦略;"
            "past-question-strategy:過去問の使い方;"
            "affiliate-problem-books:おすすめ問題集;"
            "affiliate-textbooks-recommend:おすすめテキスト;"
            f"{amazon('4426616573')}:ユーキャン予想模試（Amazon）;"
            f"{amazon('4415241077')}:成美堂過去6回（Amazon）;"
            f"{amazon('4867881015')}:労基団連問題集（Amazon）"
        ),
        "key_points": (
            "ユーキャン 重要過去問&予想模試;"
            "成美堂 過去6回問題集;"
            "労基団連 試験問題集;"
            "模試・予想問題の位置づけ;"
            "模試スケジュールの具体例"
        ),
    },
    "affiliate-beginner-material-set": {
        "title": "第二種衛生管理者の初学者向け教材セット3選【テキスト・要点・演習2026】",
        "meta_description": (
            "第二種衛生管理者の初学者向け教材セット3選。"
            "TACスッキリ·成美堂集中レッスン·ユーキャン過去問を比較。"
            "テキスト1冊から始める購入順と週次配分を解説。"
        ),
        "lead": (
            "第二種衛生管理者試験の初学者教材は、"
            "テキスト1冊で全体像を掴み、要点整理と演習を段階的に追加する方法が扱いやすいです。"
            "本試験は30問·約3時間·3科目（労働生理·労働衛生·関係法令）で、"
            "総合180点かつ各科目40点以上が合格基準です（要項で再確認）。"
            "本記事では2026年度版の教材3冊を、初学者の学習フェーズ別に比較します。"
            "価格は購入前にAmazonで必ずご確認ください。"
        ),
        "priority": "355",
        "original_note": f"Amazon tag={TAG}。4300121273 / 4415241069 / 4426616573。",
        "user_intent": "第二種初学者が最初に揃えるテキスト·要点·演習の3冊を比較して決めたい。",
        "action_items": (
            "要項で30問·180点·各40点を1行メモする;"
            "3冊の学習フェーズを比較表で確認する;"
            "7月にテキスト1冊を決め8月に演習1冊を追加する;"
            "週5〜8時間をテキスト4h+演習4hに固定する;"
            "study-plan-beginnerで月次計画をカレンダー固定する"
        ),
        "revision_note": "2026-06-15: 初学者セット比較として全面リライト·published",
        "sections": [
            (
                "初学者向け教材の位置づけ",
                "初学者は「要項確認→テキスト1冊→演習1冊→無料演習→30問模試」の順で段階投入します。"
                f"出題範囲·合格基準は{OFFICIAL}の要項で先に1枚にまとめ、"
                "学習カレンダーと申込手続きカレンダーは分離してください。"
                "3冊を同時購入せず、テキスト到着後2週間で使い心地を確認してから演習を追加するのが定番です。"
                "当サイトの分野別演習10問で現在地を記録してから購入すると、教材選びの失敗が減ります。",
            ),
            (
                "3冊の選び方（フェーズ別）",
                "全体像を1冊でつかみたい人は「スッキリわかる テキスト&問題集」、"
                "要点整理から演習比重を上げたい人は「集中レッスン」、"
                "テキスト読了後の演習1冊としては「ユーキャン 重要過去問&予想模試」が向きます。"
                "集中レッスンはテキスト本体の代替にはならない点に注意し、"
                "いずれも2026年度版表記を購入前に確認してください。"
                "比較表で学習フェーズと週次時間に合う1冊から始め、段階的に追加してください。",
            ),
            (
                "1位：TACスッキリの特徴",
                "2026年度版 スッキリわかる 第2種衛生管理者 テキスト&問題集"
                "（TAC出版·1,650円税込参考·448ページ·B5判）は、"
                "衛生管理未経験の初学者が最初に手に取りやすい定番1冊です。"
                "図解中心で労働生理·労働衛生·関係法令の輪郭を把握しやすく、"
                "章末演習で理解→確認のサイクルが回しやすい構成です。"
                "おすすめテキストの記事でも紹介していますが、"
                "本記事では初学者の第1冊としての購入順を説明します。\n\n"
                "向いている人：図解から三科目を1冊で進めたい人。",
            ),
            (
                "2位：成美堂集中レッスンの特徴",
                "第2種衛生管理者 集中レッスン '26年版"
                "（成美堂出版·1,540円税込参考·208ページ·B5判）は、"
                "要点整理から演習へ移りたい人向けです。"
                "レッスン形式で論点を短時間復習でき、"
                "成美堂の過去6回問題集へのステップアップがしやすい構成です。"
                "ただしテキスト本体の代替にはならないため、"
                "スッキリや合格教本で第1周を終えたあとの要点整理用として使うのが定番です。"
                "仕事終わりの30分学習と相性がよい1冊です。\n\n"
                "向いている人：テキスト第1周後に要点を短時間で復習したい人。",
            ),
            (
                "3位：ユーキャン過去問の特徴",
                "2026年版 ユーキャンの第2種衛生管理者 重要過去問&予想模試"
                "（ユーキャン / 自由国民社·1,760円税込参考·288ページ·B5判）は、"
                "テキスト読了後に演習量を確保したい人向けです。"
                "重要過去問で本試験形式に慣れ、予想模試で直前の総仕上げができる構成です。"
                "テキスト1冊＋問題集1冊の2冊構成に組み込みやすく、"
                "affiliate-problem-booksの記事と併用すると演習計画が立てやすくなります。"
                "購入前に第二種専用（30問·3科目）かを表紙で確認してください。\n\n"
                "向いている人：テキスト第1周完了後に演習1冊を追加したい人。",
            ),
            (
                "購入順序の具体例（6月開始）",
                "例：6/15要項30分→6/21演習10問→7/5（土）テキスト1冊決定→"
                "8/2（土）演習1冊追加→9月から30問·180分模試を月1回。"
                "テキスト到着後2週間で第1章+演習10問を試し、"
                "読みにくければ別冊へ切り替えてください。"
                "申込締切と受験手数料は学習量と混同しないよう、"
                "手続きカレンダーに先に登録しておきましょう。"
                "study-plan-beginner記事で週次時間を先に固定すると、"
                "テキスト到着前に買いすぎて使い切れないリスクを減らせます。"
                "当サイトの無料演習10問で現在地を記録してから購入する習慣も有効です。",
            ),
            (
                "購入前チェックリスト",
                "購入前に以下を確認してください。\n"
                "・2026年度版（最新版）か\n"
                "・第二種衛生管理者試験専用か（第一種100問教材と混同しない）\n"
                "・集中レッスンをメインテキストにしない計画か\n"
                "・Amazon在庫·価格（執筆時点と異なる場合あり）\n"
                "・週5時間以上確保できるか（不足ならstudy-plan-6months記事を検討）\n"
                "・購入直前にAmazon販売ページで版表記·在庫状況を再確認してください。"
                "3冊同時購入は避け、テキスト到着後2週間の試用結果で演習を追加する順序を守ってください。",
            ),
        ],
        "faqs": [
            (
                "初学者は何を最初に買うべきですか？",
                "要項確認のあとテキスト1冊です。"
                "たとえば6/15要項30分→6/21演習10問→7/5に本記事の3冊から1冊、"
                "8/2に演習1冊、の順が定番です。"
                "3冊同時購入は避けて段階投入してください。"
                "テキスト到着後2週間で第1章を試し、"
                "読み進めにくければ別冊へ切り替える判断も早めに行いましょう。",
            ),
            (
                "集中レッスンだけで独学できますか？",
                "要点整理と短時間復習には向きますが、"
                "テキスト本体の代替にはなりません。"
                "スッキリや合格教本で第1周を終えたあと、"
                "弱点分野の要点整理用として使うのがおすすめです。"
                "集中レッスン単体では演習量が不足しやすいため、"
                "ユーキャン過去問など演習1冊を別途追加する計画を立ててください。",
            ),
            (
                "テキスト記事と初学者記事の違いは何ですか？",
                "テキスト記事は3冊のテキスト比較、"
                "本記事は初学者の学習フェーズ（全体像→要点→演習）に沿った3冊の位置づけを説明しています。"
                "テキストを1冊決めたうえで、演習追加のタイミングを本記事で整理してください。",
            ),
        ],
        "related_links": (
            "study-plan-beginner:初学者向け学習計画;"
            "dokugaku-guide:独学合格ガイド;"
            "past-question-strategy:過去問の使い方;"
            "affiliate-textbooks-recommend:おすすめテキスト;"
            "affiliate-problem-books:おすすめ問題集;"
            "goukaku-kijun:合格基準と足切り;"
            f"{amazon('4300121273')}:TACスッキリ（Amazon）;"
            f"{amazon('4415241069')}:成美堂集中レッスン（Amazon）;"
            f"{amazon('4426616573')}:ユーキャン過去問（Amazon）"
        ),
        "key_points": (
            "TACスッキリ テキスト&問題集;"
            "成美堂 集中レッスン;"
            "ユーキャン 重要過去問&予想模試;"
            "購入順序の具体例;"
            "初学者向け教材の位置づけ"
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
        row["fact_checked_at"] = "2026-06-15"
        row["content_status"] = "published"
        row["related_links"] = cfg["related_links"]
        row["key_points"] = cfg["key_points"]
        for i, (heading, body) in enumerate(cfg["sections"], start=1):
            row[f"section_{i}_heading"] = heading
            row[f"section_{i}_body"] = body.strip()
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
