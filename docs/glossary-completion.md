# 用語解説 267語 完了チェックリスト

## 完了（2026-05-22）

- [x] 用語 **267語**（第4弾50語＋気集＋既存）
- [x] 全語 `exam_points` / `common_mistakes` 整備（汎用テンプレート 0 件）
- [x] 品質仕上げ（`enrich_glossary_quality_finish.py`）— 試験整理表・比較表・独自解説
- [x] 過去問リンク **267/267**（`match`: primary / related / fallback、ラベルに種別表示）
- [x] `terms/*.html` に学習のつながり（まとめ・過去問・ガイド）
- [x] `tools/build_all.py` に品質仕上げステップを組み込み

### 品質監査

```bash
python3 tools/audit_glossary_quality.py
```

## 一括ビルド

```bash
python3 tools/build_all.py
```

## 用語のみ再生成

```bash
python3 tools/populate_glossary_related_terms.py
python3 tools/build_term_question_links.py
python3 tools/sync_term_related_questions.py
cd eisei-articles && python3 build.py && cd ..
python3 tools/build_glossary_pages.py
```

## デプロイ

`main` への push で GitHub Actions（Deploy GitHub Pages）が実行されます。  
Settings → Pages → Source が **GitHub Actions** であることを確認してください。
