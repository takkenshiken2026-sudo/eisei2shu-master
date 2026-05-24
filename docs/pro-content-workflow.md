# 専門家品質コンテンツ（用語・試験ガイド）

## 対象

| 種別 | 件数 | データ | 出力 |
|------|------|--------|------|
| 用語詳細 | 267 | `data/glossary_terms.csv` | `terms/*.html` |
| 試験ガイド | 100 | `data/guide_articles.csv` | `articles/*/index.html` |

## 一括更新

```bash
python3 tools/apply_glossary_handmade_rewrite.py   # MD の表・誤り肢（手作り）
python3 tools/apply_pro_content_all.py             # CSV / ガイド本文の専門家品質化
python3 tools/build_glossary_pages.py
python3 tools/build_article_pages.py
```

`tools/build_all.py` に統合済み（手作り → pro → リンク生成 → HTML）。

## 品質の柱（用語）

1. **まず押さえる要点** … 試験での位置づけを明示
2. **具体例** … 職場・過去問のイメージ（`summary_example`）
3. **選択肢で問われやすい点** … 誤り肢の型を列挙
4. **覚え方** … 核心・比較・直前チェック（箇条書き）
5. **FAQ 4件** … 学習目的・ひっかけ・関連語・実務

手作りデータ（`tools/handmade/`）の tips を優先し、試験内容の正確性を担保します。

## 個別の手直し

- 用語の具体例を厚くする: `tools/reader_friendly_lib.py` の `CONCRETE_EXAMPLES`
- 用語の誤り肢: `tools/handmade/glossary_*_data.py` の該当 `I(...)`
- ガイドの本文: `data/guide_articles.csv` を直接編集後、`build_article_pages.py`
