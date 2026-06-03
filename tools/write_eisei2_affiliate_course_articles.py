#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write affiliate course briefs + CSV rows for eisei2shu-master (A8 SMART / オンスク)."""

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

A8_SMART = (
    "https://px.a8.net/svt/ejp?a8mat=4B3TF0+DUBUVU+4LOQ+BW0YB"
    "&a8ejpredirect=https%3A%2F%2Fwww.joho-gakushu.or.jp%2Feiseikanrisya%2F"
    "%3Futm_source%3DAffi%26utm_medium%3Dlist%26utm_campaign%3D01%26_gl%3D1*3gogtr*_gcl_au*NDM5NDE0NjUzLjE3NzkzNDY4MTQ."
)
A8_ONSUKU = (
    "https://px.a8.net/svt/ejp?a8mat=4B3TF0+DUXAHM+408S+BW0YB"
    "&a8ejpredirect=https%3A%2F%2Fonsuku.jp%2Ftraining%2Feisei2"
)

PRICE_CHECKED = "2026-06-03"


def course(
    rank: int,
    name: str,
    provider: str,
    *,
    price_yen: int = 0,
    price_label: str = "",
    billing_type: str = "lump",
    duration: str = "",
    lecture_hours: str = "",
    support: str = "",
    a8_url: str = "",
    image_file: str = "",
    for_who: str = "",
    highlights: list[str],
) -> dict:
    product: dict = {
        "rank": rank,
        "offer_type": "course",
        "name": name,
        "provider": provider,
        "billing_type": billing_type,
        "a8_url": a8_url,
        "image_file": image_file,
        "for_who": for_who,
        "highlights": highlights,
    }
    if price_label:
        product["price_label"] = price_label
    elif price_yen:
        product["price_yen"] = price_yen
    if duration:
        product["duration"] = duration
    if lecture_hours:
        product["lecture_hours"] = lecture_hours
    if support:
        product["support"] = support
    return product


BRIEFS_DATA = {
    "affiliate-smart-vs-onsuku": {
        "slug": "affiliate-smart-vs-onsuku",
        "theme_key": "smart-vs-onsuku",
        "search_intent": "第二種衛生管理者向けにSMART合格講座とオンスクを比較したい",
        "title": "第二種衛生管理者 SMART合格講座とオンスク比較【2026】料金・向き不向き",
        "layout": "product-comparison",
        "asp_primary": "a8",
        "comparison_kind": "courses",
        "comparison_title": "オンライン講座2選（比較）",
        "price_disclaimer": (
            f"料金・受講条件は執筆時点（{PRICE_CHECKED}）の各公式ページ参考です。"
            "申込前に必ず最新の料金・キャンペーンを確認してください。"
        ),
        "products": [
            course(
                1,
                "SMART合格講座（第二種衛生管理者）",
                "情報学習支援協会",
                price_yen=25300,
                billing_type="lump",
                duration="視聴3年間",
                lecture_hours="約7.5時間",
                support="SMART答練・進捗管理",
                a8_url=A8_SMART,
                image_file="eisei2-smart-goukaku.jpg",
                for_who="買い切りで動画と演習をまとめて使いたい人",
                highlights=[
                    "第二種向け動画約7.5時間＋SMART答練",
                    "買い切り25,300円（税込）で視聴3年",
                    "分割払い対応（公式ページ参照）",
                ],
            ),
            course(
                2,
                "オンスク.JP 衛生管理者オンライン通信講座",
                "オンスク.JP",
                price_label="月額1,078〜1,628円（税込・ウケホーダイ）",
                billing_type="monthly",
                duration="月額または一括パック",
                lecture_hours="講義50回・約4.5時間",
                support="練習536問・進捗管理・復習機能",
                a8_url=A8_ONSUKU,
                image_file="eisei2-onsuku-eisei2.jpg",
                for_who="短期間・低コストで演習量を確保したい社会人",
                highlights=[
                    "講義50回＋練習536問",
                    "ウケホーダイ月額1,078〜1,628円（税込）",
                    "3か月パック税込4,884円〜（2026-06-03時点）",
                ],
            ),
        ],
        "operator_note": f"A8 SMART・オンスク。価格確認日 {PRICE_CHECKED}。",
    },
    "affiliate-smart-course-guide": {
        "slug": "affiliate-smart-course-guide",
        "theme_key": "smart-course-guide",
        "search_intent": "第二種衛生管理者向けSMART合格講座の料金・内容・進め方を知りたい",
        "title": "第二種衛生管理者 SMART合格講座の口コミ・料金【2026】特徴と進め方",
        "layout": "product-comparison",
        "asp_primary": "a8",
        "comparison_kind": "courses",
        "comparison_title": "SMART合格講座（第二種）",
        "price_disclaimer": (
            f"料金・受講条件は執筆時点（{PRICE_CHECKED}）の公式ページ参考です。"
            "申込前に必ず最新情報を確認してください。"
        ),
        "products": [
            course(
                1,
                "SMART合格講座（第二種衛生管理者）",
                "情報学習支援協会",
                price_yen=25300,
                billing_type="lump",
                duration="視聴3年間",
                lecture_hours="約7.5時間",
                support="SMART答練・進捗管理",
                a8_url=A8_SMART,
                image_file="eisei2-smart-goukaku.jpg",
                for_who="動画で3分野の全体像をつかみ、答練で演習したい人",
                highlights=[
                    "第二種向けSMARTビデオ講座",
                    "SMART答練で過去問・予想問題を解説",
                    "視聴3年・分割払い可",
                ],
            ),
        ],
        "operator_note": f"A8 SMART 第二種。確認日 {PRICE_CHECKED}。",
    },
}


CSV_ROWS = {
    "affiliate-smart-vs-onsuku": {
        "meta_description": (
            "第二種衛生管理者のオンライン講座「SMART合格講座」（25,300円・3年視聴）と"
            "オンスク（月額1,078円〜）を料金・動画・問題数・向き不向きで比較。"
            "2026年6月時点の公式情報に基づき解説。"
        ),
        "lead": (
            "第二種衛生管理者試験の独学で、動画による理解補強や演習量の確保を検討している方へ。"
            "本記事では買い切りのSMART合格講座と月額型のオンスク.JPを、"
            "料金・講義量・演習の観点から比較します。"
            "料金は執筆時点の公式ページ参考です。申込前に各サイトで最新条件を確認してください。"
        ),
        "user_intent": (
            "第二種向けSMART合格講座とオンスクの違いを把握し、"
            "学習期間と予算に合う講座を1つ選びたい。"
        ),
        "action_items": (
            "比較表で料金と演習量を確認する;"
            "自分の学習期間に合う講座を絞る;"
            "二衛マスターの過去問で理解度をチェックする"
        ),
        "revision_note": f"{PRICE_CHECKED}: テンプレ構成に合わせて本文全面リライト",
        "original_note": (
            f"A8 SMART 25,300円・オンスク月額1,078〜1,628円（税込）。確認日 {PRICE_CHECKED}。"
        ),
        "key_points": "2講座の比較ポイント;独学との併用;受講期間の目安",
        "sections": [
            (
                "講座選びの基準（第二種向け）",
                "第二種衛生管理者向け講座を選ぶときは、次の4点を確認します。\n\n"
                "- 労働生理・労働衛生・関係法令の3分野を動画でカバーしているか\n"
                "- SMART答練や練習問題など演習量が確保できるか\n"
                "- 買い切りか月額かが学習期間と合うか\n"
                "- 視聴期限・解約条件が仕事のペースに合うか\n\n"
                "講座はテキストや過去問の代わりではなく、独学の弱点補強として位置づけます。",
            ),
            (
                "2講座の比較の見方",
                "SMART合格講座は買い切り25,300円（税込）で視聴3年、動画約7.5時間＋SMART答練がセットです。"
                "オンスク.JPはウケホーダイ月額1,078〜1,628円（税込）で、講義50回・練習536問を回せます。\n\n"
                "長期で何度も見返す計画ならSMART、試験3〜4か月前から短期集中するならオンスクが選ばれやすい傾向です。",
            ),
            (
                "SMART合格講座（第二種）の特徴",
                "SMART合格講座（第二種衛生管理者）は、情報学習支援協会の買い切り型講座です。"
                "SMARTビデオ講座で3分野を約7.5時間で学び、SMART答練で過去問・予想問題を一問一答形式で復習できます。"
                "受講料25,300円（税込）、視聴期限は申込日から3年間です（2026-06-03時点・公式ページ参照）。\n\n"
                "向いている人：動画で全体像を一度通したい人、答練付きで演習量を確保したい人。",
            ),
            (
                "オンスク.JP講座の特徴",
                "オンスク.JP 衛生管理者オンライン通信講座は、月額型の通信講座です。"
                "講義動画50回（約4.5時間）に加え、練習536問と進捗・復習機能が付いています。"
                "ウケホーダイプランは月額1,078〜1,628円（税込）、3か月パックは税込4,884円〜です（2026-06-03時点）。\n\n"
                "向いている人：試験直前数か月でコストを抑えつつ演習量を増やしたい社会人。",
            ),
            (
                "学習期間別の総額目安",
                "試験まで6か月ある場合、SMART合格講座（25,300円・3年視聴）は月あたり約4,217円相当。"
                "動画を何度も見返す計画ならコスパが出やすいです。\n\n"
                "試験まで3か月なら、オンスクの3か月パック（税込4,884円〜）や"
                "月額1,078円プランの方が総額を抑えやすいケースがあります。"
                "ただし演習の主戦場は過去問なので、講座料金＋テキストの合計も見てください。",
            ),
            (
                "二衛マスター（無料）との併用",
                "講座は「理解」、二衛マスターの過去問・一問一答は「本試験形式の演習」に使い分けます。\n\n"
                "例（週5日・1日60分）：\n"
                "- 月〜水：講座動画1〜2本\n"
                "- 木：過去問を分野別に10問\n"
                "- 金：間違えた論点を用語解説で整理\n\n"
                "講座で学んだ章を同週の過去問で確認するサイクルが効果的です。",
            ),
            (
                "申込前のチェックリスト",
                "申込前に各公式ページで以下を確認してください。\n"
                "・最新の受講料（キャンペーン・分割払い条件）\n"
                "・視聴期限・解約・自動更新の有無\n"
                "・第二種の3分野がカリキュラムに含まれるか\n"
                "・スマホ視聴・オフライン視聴の可否\n"
                "・自分の弱点分野と講座の章立てが合うか",
            ),
        ],
        "faqs": [
            (
                "SMART合格講座とオンスク、第二種だけ受けるならどちらが安いですか？",
                "受講3か月ならオンスクの月額・3か月パックの方が総額を抑えやすいことが多いです。"
                "6か月以上かけて何度も動画を見返すならSMARTの買い切りも検討余地があります。"
                "最新料金は必ず公式ページで確認してください。",
            ),
            (
                "オンスクのライトプランとスタンダード、第二種受験ではどちらを選べばよいですか？",
                "演習536問と進捗管理まで使うならスタンダード相当のプランが無難です。"
                "動画だけ軽く見たい短期利用ならライトでも足りる場合があります。"
                "申込前に各プランの収録内容を公式ページで比較してください。",
            ),
            (
                "講座だけで合格できますか？",
                "講座だけでは演習量が不足しがちです。"
                "SMART答練やオンスクの練習問題に加え、二衛マスターの過去問で本試験形式の演習を重ねる構成を推奨します。",
            ),
        ],
    },
    "affiliate-smart-course-guide": {
        "meta_description": (
            "第二種衛生管理者向けSMART合格講座を料金25,300円・3年視聴・動画約7.5時間・"
            "SMART答練の観点から解説。向き不向きと学習の進め方、オンスクとの違いも整理。"
        ),
        "lead": (
            "情報学習支援協会のSMART合格講座は、第二種衛生管理者試験向けの買い切りオンライン講座として人気があります。"
            "本記事では2026年6月時点の公式情報に基づき、料金・講座内容・向いている人・学習の進め方を整理します。"
            "価格・機能は申込前に必ず公式サイトでご確認ください。"
        ),
        "user_intent": (
            "第二種向けSMART合格講座の料金・内容・視聴期限を把握し、"
            "独学や過去問演習とどう組み合わせるか判断したい。"
        ),
        "action_items": (
            "公式ページで最新料金を確認する;"
            "講座動画で3分野の全体像をつかむ;"
            "二衛マスターの過去問で本試験形式の演習を重ねる"
        ),
        "revision_note": f"{PRICE_CHECKED}: テンプレ構成に合わせて本文全面リライト",
        "original_note": f"A8 SMART 第二種 25,300円（税込）。確認日 {PRICE_CHECKED}。",
        "key_points": "料金・受講期間;SMART答練の位置づけ;独学との併用",
        "sections": [
            (
                "SMART合格講座が向いている人",
                "第二種衛生管理者向けSMART合格講座が向いているのは、次のような方です。\n\n"
                "- 独学でテキストは読めるが、動画で一度全体像を通したい\n"
                "- SMART答練で過去問・予想問題の解説を見ながら演習したい\n"
                "- 買い切り25,300円（税込）で3年間繰り返し視聴したい\n"
                "- 仕事が忙しく、テキストだけでは学習習慣が続きにくい\n\n"
                "逆に、すでに過去問演習で高得点が取れている場合は講座なしでも十分なケースがあります。",
            ),
            (
                "料金・受講期間（2026年6月時点）",
                "第二種衛生管理者 SMART合格講座の受講料は25,300円（税込）です（2026-06-03・公式ページ確認）。"
                "視聴期限は申込日から3年間。分割払いにも対応しています。\n\n"
                "キャンペーン価格や分割条件は変動するため、申込前に必ず公式ページで最新情報を確認してください。",
            ),
            (
                "講座内容：SMARTビデオ講座とSMART答練",
                "SMARTビデオ講座は、労働生理・労働衛生・関係法令の3分野を動画で学べます（合計約7.5時間）。"
                "SMART答練では、過去問・予想問題を一問一答形式で解き、解説動画で復習できます。\n\n"
                "テキストで理解した論点を、答練で「本試験形式のアウトプット」に移す流れが作りやすい構成です。",
            ),
            (
                "おすすめの学習の進め方（3〜6ヶ月例）",
                "1〜2か月目：テキストまたはSMART動画で3分野の全体像を把握\n"
                "3〜4か月目：SMART答練＋二衛マスター過去問（分野別）\n"
                "5〜6か月目：過去問通し演習＋弱点分野の動画復習\n\n"
                "週のうち2〜3日は講座、残りは過去問演習に充てるとバランスが取りやすいです。",
            ),
            (
                "オンスクなど他講座との違い",
                "オンスク.JPは月額1,078〜1,628円（税込）のサブスク型で、短期集中向きです。"
                "SMARTは買い切り25,300円（税込）で3年視聴でき、答練付きの演習型講座です。\n\n"
                "2講座の詳細比較は SMARTとオンスク比較 の記事を参照してください。",
            ),
            (
                "二衛マスター（無料）との併用",
                "二衛マスターの過去問・一問一答は無料で利用できます。"
                "SMARTで理解した章を、同週の過去問で確認するサイクルが効果的です。"
                "間違えた設問は用語解説で補強し、1週間後に解き直してください。",
            ),
            (
                "申込前のチェックリスト",
                "申込前に公式ページで以下を確認してください。\n"
                "・最新の受講料と分割払い条件\n"
                "・視聴期限（3年）と動作環境\n"
                "・SMART答練の収録範囲\n"
                "・自分の学習計画（3か月／6か月）と講座の役割分担",
            ),
        ],
        "faqs": [
            (
                "SMART合格講座の第二種はいくらですか？",
                "2026年6月3日時点の公式ページでは25,300円（税込）です。"
                "キャンペーンや分割条件は変わることがあるため、申込前に必ず公式サイトで確認してください。",
            ),
            (
                "視聴期限はどのくらいですか？",
                "申込日から3年間です（2026-06-03時点・公式ページ）。"
                "一度申し込めば、合格後の復習や再受験の予習にも使えます。",
            ),
            (
                "SMART答練だけでも使えますか？",
                "答練は演習向けの機能ですが、初めての論点は動画講座で理解してから使う方が効率的です。"
                "動画→答練→二衛マスター過去問、の順がおすすめです。",
            ),
        ],
    },
}


COURSE_AFFILIATE_RELATED: dict[str, str] = {
    "affiliate-smart-vs-onsuku": (
        "dokugaku-guide:独学合格ガイド;"
        "past-question-strategy:過去問の使い方;"
        "tsushin-kouza-vs-dokugaku:通信講座と独学の比較;"
        "affiliate-smart-course-guide:SMART合格講座の詳細解説"
    ),
    "affiliate-smart-course-guide": (
        "dokugaku-guide:独学合格ガイド;"
        "past-question-strategy:過去問の使い方;"
        "tsushin-kouza-vs-dokugaku:通信講座と独学の比較;"
        "affiliate-smart-vs-onsuku:SMARTとオンスクの比較"
    ),
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
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
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
        for key in (
            "meta_description",
            "lead",
            "user_intent",
            "action_items",
            "revision_note",
            "original_note",
            "key_points",
        ):
            if key in cfg:
                row[key] = cfg[key]
        row["fact_checked_at"] = PRICE_CHECKED
        row["content_status"] = "published"
        for i, (heading, body) in enumerate(cfg["sections"], start=1):
            row[f"section_{i}_heading"] = heading
            row[f"section_{i}_body"] = body
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

    for row in rows:
        slug = row.get("slug", "")
        if slug in COURSE_AFFILIATE_RELATED:
            row["related_links"] = COURSE_AFFILIATE_RELATED[slug]
            print(f"patched related_links: {slug}")

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
