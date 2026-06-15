#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""学習系ガイドへ公開済み affiliate 比較記事の導線を追加する（第二種衛生管理者）。"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "guide_articles.csv"

AFFILIATE_TITLES = {
    "affiliate-textbooks-recommend": (
        "第二種衛生管理者のおすすめ参考書・テキスト3選【2026年度版・独学】"
    ),
    "affiliate-problem-books": (
        "第二種衛生管理者のおすすめ問題集3選【過去問・予想模試2026】"
    ),
    "affiliate-mock-exam-materials": (
        "第二種衛生管理者試験の模試・予想問題3選【30問本番形式2026】"
    ),
    "affiliate-beginner-material-set": (
        "第二種衛生管理者の初学者向け教材セット3選【テキスト・要点・演習2026】"
    ),
}

BODY = {
    "affiliate-textbooks-recommend": (
        "テキスト1冊は、affiliate-textbooks-recommend でスッキリ·合格教本·村中テキストの3冊を比較してから固定すると、"
        "第二種30問·3科目の演習計画に組み込みやすくなります。"
    ),
    "affiliate-problem-books": (
        "テキスト第1周後の演習1冊は、affiliate-problem-books でユーキャン·成美堂·労基団連の3冊から選ぶと、"
        "30問本番形式の演習量を確保しやすくなります。"
    ),
    "affiliate-mock-exam-materials": (
        "本番形式の模試1冊は、affiliate-mock-exam-materials でユーキャン予想模試·成美堂過去6回·"
        "労基団連問題集の3冊を比較してから固定すると、"
        "13:30開始·30問·180分の模試回数と使い分けが整理しやすくなります。"
    ),
    "affiliate-beginner-material-set": (
        "初学者の第1冊は、affiliate-beginner-material-set でスッキリ·集中レッスン·ユーキャン過去問の3冊を"
        "学習フェーズ別に比較してから固定すると、"
        "テキスト→演習の段階投入がぶれにくくなります。"
    ),
}

GUIDE_AFFILIATE: dict[str, tuple[str, int]] = {
    "dokugaku-guide": ("affiliate-textbooks-recommend", 2),
    "study-plan-beginner": ("affiliate-beginner-material-set", 2),
    "study-plan-3months": ("affiliate-textbooks-recommend", 3),
    "study-plan-6months": ("affiliate-textbooks-recommend", 3),
    "study-plan-working": ("affiliate-textbooks-recommend", 3),
    "textbook-erabikata": ("affiliate-textbooks-recommend", 2),
    "textbook-osusume": ("affiliate-textbooks-recommend", 2),
    "past-question-strategy": ("affiliate-problem-books", 2),
    "kakomon-nannennbun": ("affiliate-problem-books", 2),
    "past-questions-by-field": ("affiliate-problem-books", 2),
    "field-law-past-question-focus": ("affiliate-problem-books", 2),
    "field-rights-past-question-focus": ("affiliate-problem-books", 2),
    "field-limit-past-question-focus": ("affiliate-problem-books", 2),
    "mock-exam-how-to": ("affiliate-mock-exam-materials", 3),
    "ichimon-practice": ("affiliate-problem-books", 2),
    "timed-practice": ("affiliate-mock-exam-materials", 3),
    "time-limit-strategy": ("affiliate-mock-exam-materials", 2),
}


def _split_related(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(";") if x.strip()]


def _append_related(value: str, token: str) -> str:
    parts = _split_related(value)
    slug = token.split(":", 1)[0]
    if any(p.split(":", 1)[0] == slug for p in parts):
        return ";".join(parts)
    parts.append(token)
    return ";".join(parts)


def _append_body(body: str, aff_slug: str) -> str:
    sentence = BODY[aff_slug]
    if aff_slug in (body or ""):
        return body
    text = (body or "").rstrip()
    if not text:
        return sentence
    if not text.endswith("。"):
        text += "。"
    return text + sentence


def apply_guide_updates(rows: list[dict[str, str]]) -> int:
    by_slug = {r["slug"]: r for r in rows}
    changed = 0
    for slug, (aff_slug, sec_n) in GUIDE_AFFILIATE.items():
        row = by_slug.get(slug)
        if not row or (row.get("content_status") or "").strip() != "published":
            continue
        body_key = f"section_{sec_n}_body"
        old_body = row.get(body_key, "")
        new_body = _append_body(old_body, aff_slug)
        if new_body != old_body:
            row[body_key] = new_body

        token = f"{aff_slug}:{AFFILIATE_TITLES[aff_slug]}"
        new_rl = _append_related(row.get("related_links", ""), token)
        if new_rl != row.get("related_links", "") or new_body != old_body:
            row["related_links"] = new_rl
            changed += 1
    return changed


def main() -> None:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if not fieldnames:
        raise SystemExit("guide_articles.csv: no header")

    changed = apply_guide_updates(rows)

    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Guide funnel: {len(GUIDE_AFFILIATE)} targets, {changed} row(s) updated")


if __name__ == "__main__":
    main()
