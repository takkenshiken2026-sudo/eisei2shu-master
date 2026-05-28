# 用語詳細記事：読みやすさ改善

## 対象

`terms/{slug}.html`（`data/glossary_terms.csv` から `tools/build_glossary_pages.py` が生成）

## 反映内容

| 項目 | CSV 列 | ページ上の見出し |
|------|--------|------------------|
| やさしい要点 | `short_def` | まず押さえる要点 |
| 具体例 | `summary_example` | まず押さえる要点（枠内） |
| 覚え方 | `memory_tip`（改行区切り） | 覚え方・整理のコツ |
| FAQ 4件 | `faq_1`〜`faq_4` | よくある質問 |

## 一括更新

```bash
python3 tools/apply_glossary_reader_friendly.py
python3 tools/build_glossary_pages.py
```

`tools/build_all.py` にも組み込み済み（手作りリライトの直後）。

## 個別の手直し

- 具体例を厚くする: `tools/reader_friendly_lib.py` の `CONCRETE_EXAMPLES` に slug を追加
- 1語だけ CSV を編集したあと: `build_glossary_pages.py` のみ再実行
