#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公開コンテンツの誤字・重複・表崩れ・リンク切れパターンを検証する。"""
from __future__ import annotations

import csv
import io
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.pro_content.guide_writer import is_boilerplate_lead, is_generic_faq  # noqa: E402
from tools.validate_csv import GUIDE_BROKEN_LINK_MARKERS, OPERATOR_CONTENT_FRAGMENTS  # noqa: E402

GUIDE_CSV = ROOT / "data" / "guide_articles.csv"

# 既知の誤字・表記ゆれ
KNOWN_TYPOS: list[tuple[str, str]] = [
    ("公…", "FAQ回答の途中切れ"),
]

# 同一文字の3連続以上（数字・記号を除く）
DUP_CHAR_RE = re.compile(r"([\u3040-\u9fff\u30a0-\u30ff\u4e00-\u9fff])\1{2,}")

# 表データが段落に潰れている兆候（ヘッダ語の連続）
FLAT_TABLE_RE = re.compile(
    r"(項目内容|要件内容|義務内容|頻出度テーマ|科目割合|対策の種類内容|"
    r"プランA|プランB|タイミングやること|重症度旧称|環境計算式)"
)


@dataclass
class Issue:
    level: str
    source: str
    message: str

    def format(self) -> str:
        return f"[{self.level}] {self.source} - {self.message}"


class ContentQualityValidator:
    def __init__(self) -> None:
        self.issues: list[Issue] = []

    def error(self, source: str, message: str) -> None:
        self.issues.append(Issue("ERROR", source, message))

    def warn(self, source: str, message: str) -> None:
        self.issues.append(Issue("WARN", source, message))

    def check_text(self, source: str, text: str) -> None:
        if not text:
            return
        for typo, reason in KNOWN_TYPOS:
            if typo in text and typo != "necchuysho":
                self.warn(source, f"疑わしい文言「{typo}」: {reason}")
        for fragment, reason in OPERATOR_CONTENT_FRAGMENTS:
            if fragment in text:
                self.error(source, f"公開禁止「{fragment}」: {reason}")
        for fragment in GUIDE_BROKEN_LINK_MARKERS:
            if fragment in text:
                self.error(source, f"壊れたリンク形式: {fragment}")
        m = DUP_CHAR_RE.search(text)
        if m:
            self.error(source, f"同一文字の重複: {m.group(0)!r}")
        if FLAT_TABLE_RE.search(text) and "[table]" not in text and "|" not in text:
            self.error(source, "表データが段落に潰れています（[table]形式への変換が必要）")
        parts = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        dupes = [p for p in parts if len(p) >= 40 and parts.count(p) >= 2]
        for dup in dupes[:1]:
            self.error(source, f"同一段落の重複: {dup[:40]}…")

    def validate_guide_csv(self) -> None:
        rows = list(csv.DictReader(GUIDE_CSV.open(encoding="utf-8-sig", newline="")))
        for idx, row in enumerate(rows, start=2):
            slug = (row.get("slug") or "").strip()
            source = f"guide_articles.csv:{idx} ({slug})"
            lead = row.get("lead") or ""
            if is_boilerplate_lead(lead):
                self.error(source, "lead に無意味な定型文が残っています")
            if is_generic_faq(row):
                self.error(source, "faq_1 が汎用テンプレのままです")
            for col in ("lead", "meta_description", "action_items"):
                self.check_text(f"{source} {col}", row.get(col) or "")
            for n in range(1, 8):
                for kind in ("heading", "body"):
                    col = f"section_{n}_{kind}"
                    self.check_text(f"{source} {col}", row.get(col) or "")
            for n in range(1, 5):
                self.check_text(f"{source} faq_{n}_question", row.get(f"faq_{n}_question") or "")
                self.check_text(f"{source} faq_{n}_answer", row.get(f"faq_{n}_answer") or "")

    def validate_generated_articles(self) -> None:
        for path in sorted((ROOT / "articles").glob("*/index.html")):
            if path.parent.name == "chapters":
                continue
            text = path.read_text(encoding="utf-8")
            source = str(path.relative_to(ROOT))
            if "項目内容" in text and "<table>" not in text:
                self.warn(source, "HTML内に表崩れの可能性（tableタグなしで項目内容）")
            if DUP_CHAR_RE.search(text):
                self.error(source, "HTML内に同一文字の重複があります")

    def run(self) -> int:
        self.validate_guide_csv()
        self.validate_generated_articles()
        errors = [i for i in self.issues if i.level == "ERROR"]
        warnings = [i for i in self.issues if i.level == "WARN"]
        for issue in self.issues:
            print(issue.format(), file=sys.stderr if issue.level == "ERROR" else sys.stdout)
        if errors:
            print(
                f"Content quality validation failed: {len(errors)} error(s), {len(warnings)} warning(s)",
                file=sys.stderr,
            )
            return 1
        print(f"Content quality validation passed: {len(warnings)} warning(s)")
        return 0


def main() -> int:
    return ContentQualityValidator().run()


if __name__ == "__main__":
    raise SystemExit(main())
