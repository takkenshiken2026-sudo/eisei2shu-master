# 用語解説 第4弾（50語）完了チェックリスト

## 完了した作業（2026-05-22）

- [x] 過去問頻出を優先した50語の選定・追加（217〜266）＋気集（267）
- [x] `eisei-articles/articles/*.md` 詳細記事50本
- [x] `data/glossary_terms.csv` 50行追加（計266語）
- [x] `docs/glossary-article-slugs.json` 更新
- [x] `tools/enrich_batch4_glossary.py` で頻出ポイント・誤り肢を本文・CSVに反映
- [x] `terms/*.html` / `eisei-articles/dist/terms/*.html` ビルド
- [x] `docs/term-question-links.json` 再生成（70用語に過去問リンク）
- [x] 誤配置ディレクトリ `terms/terms/` 削除
- [x] サイト表記「用語解説267本」（about・カテゴリ一覧）
- [x] 優先既存語10件の充実（`tools/enrich_glossary_priority_legacy.py`）＋気集を新規追加

## 第4弾の内訳

| 分野 | 件数 |
|------|------|
| 関係法令 | 10 |
| 労働生理 | 34 |
| 労働衛生 | 6 |

## 次に修正する用語（第1〜3弾・既存216語）

`exam_points` 未整備の既存用語が **216件** あります。優先度の目安：

1. **チェックリスト未単独化** … 特別有機溶剤等、気集、許容濃度、全面換気 など
2. **バッチ2〜3で追加したが本文が薄い語** … 防護衣、グラブサンプリング、検知管 など
3. **複合用語の分割検討** … 「定期健康診断・雇入時健康診断」と第4弾「定期健康診断」の導線整理

### 推奨コマンド

```bash
# 第4弾の再充実（追記時）
python3 tools/enrich_batch4_glossary.py
cd eisei-articles && python3 build.py
cd .. && python3 tools/build_glossary_pages.py
python3 tools/build_term_question_links.py

# 全体ビルド
python3 tools/build_all.py
```

### 次バッチ作業用スクリプト

- 追加: `tools/add_50_glossary_articles_batch4.py`
- 充実: `tools/enrich_batch4_glossary.py`（既存50語向け。第1〜3弾向けに `DEFAULT_EXAM_TIPS` を拡張して流用可）
