# 二衛マスター（第二種衛生管理者試験対策・デモ）

「**二衛マスター**」は**第二種衛生管理者試験**向けの学習サイトです。画面上の「二衛」はサービス内の略表記です。

`index.html` とデータ用 JS、静的ページ（`about.html` 等）を**同一フォルダ**に置き、ローカルサーバーで開いてください（`file://` だと一部ブラウザで `localStorage` やモジュールが制限されることがあります）。

## 含まれるファイル

| ファイル | 内容 |
|---------|------|
| `index.html` | UI・アプリ本体（宅建テンプレから自動パッチ） |
| `eisei2-master-data.js` | 分野定義・過去問（令和7年度CSV取り込み・計60問。前期=year2025・後期=2026） |
| `eisei2-data-glossary.js` | 用語サンプル |
| `eisei2-data-original.js` | オリジナル演習サンプル（レベル1〜3） |
| `about.html` | このサイトについて（目的・推奨環境など） |
| `privacy-terms.html` | 利用規約・プライバシー・免責（1ページに統合） |
| `site-pages.css` | 上記静的ページ用の共通スタイル |
| `docs/glossary-terms-checklist.csv` | 用語解説の収録候補（カテゴリ・用語・解説の3列・編集用） |
| `docs/glossary-terms-checklist.md` | CSV の列説明・編集方針（人間向け） |
| `docs/question-id-url-slug-spec.md` | 問題ID・URLスラッグ規約（GitHub Pages 用・固定版） |
| `patch_build.py` | 元の `Desktop/index.html` から再生成するとき用 |
| `tools/csv_to_eisei2_master.py` | `data/*.csv` から `eisei2-master-data.js` 用の取り込み JS を生成 |
| `tools/question_slug_lib.py` | 問題ID・URLスラッグ共通ロジック（上記規約どおり） |
| `tools/build_question_pages.py` | CSV から `q/` 配下に静的問題ページを生成し、ルートの `sitemap.xml` と `robots.txt` も更新 |
| `sitemap.xml` | サイト全体の URL 一覧（ビルドで更新） |
| `robots.txt` | `Sitemap` 行を `sitemap.xml` に合わせてビルドで更新 |
| `tools/prepare_public_site.sh` | 公開用ファイルだけを `public_site/` に集約（Actions または手元確認用） |
| `.github/workflows/deploy-pages.yml` | GitHub Actions でビルド→Pages へデプロイ（`q/` をリポジトリに含めなくてよい） |

## 起動例

```bash
cd ~/Desktop/dai2shu-eisei-master
python3 -m http.server 8765
```

ブラウザで `http://127.0.0.1:8765/` を開く。

### 静的問題ページ（SEO用 `q/`）の生成

CSV を編集したあと、次で **1問1ページの HTML** と **ルートの `sitemap.xml`（全ページ）** を再生成します（既存の `q/` は上書き削除されます）。

```bash
python3 tools/build_question_pages.py
```

GitHub Pages の **プロジェクトサイト**（`https://USER.github.io/REPO/`）向けには、本番のオリジンとリポジトリ名を渡します。

```bash
python3 tools/build_question_pages.py --base-url https://USER.github.io --site-prefix REPO
```

`--base-url` は canonical・サイトマップの絶対URLに使われます。ユーザサイト直下だけなら `--site-prefix` は省略でよいです。

過去問・オリジナル用の集約 JS は従来どおり次です。

```bash
python3 tools/csv_to_eisei2_master.py -o eisei2-master-data.js
```

（`eisei2-master-data.js` を上書きする前にバックアップ推奨。）

### 公開ファイルだけを `public_site/` にまとめる

```bash
python3 tools/csv_to_eisei2_master.py -o eisei2-master-data.js
python3 tools/build_question_pages.py
bash tools/prepare_public_site.sh
```

`public_site/` 以下がそのままサーバのドキュメントルートになります（中身は従来の `eisei2shu-master-upload` と同種）。

### GitHub に載せるとき（`q/` が多すぎて Web からアップできない場合）

GitHub の画面から **大量ファイルをまとめてアップロードする方式は向きません。** 次のいずれかを使ってください。

1. **GitHub Desktop（GUI で `git push` する）**  
   ブラウザの「Upload files」とは別物で、**中身は普通の Git**です。ファイル数が多くても、コミットして **Push origin** すれば GitHub に送れます（初回は時間がかかることがあります）。  
   - **File → Add Local Repository…** で `dai2shu-eisei-master` フォルダを指定。  
   - 変更が左に並ぶので、**Summary** を書いて **Commit to main** → **Push origin**。  
   - まだ GitHub にリポジトリがない場合は **Publish repository** で作成。  
   - **GitHub Actions で公開する場合（下記パターン A）**は `.gitignore` のため **`q/` は一覧に出ずコミットされません**。コードと `data/`・`tools/`・ワークフローだけ push すればよいです。  
   - **ブランチのルートから配信する場合（パターン B）**は、`.gitignore` から `/q/` と `/sitemap.xml` を消し、先に `build_question_pages.py` を実行してから Desktop でコミットすると、`q/` もまとめて送れます。

2. **ターミナルだけで Git 操作する場合**  
   `git add -A` → `git commit` → `git push` でも同じです。

3. **GitHub Actions でデプロイ（推奨・`q/` をリポジトリに含めなくてよい）**  
   - リポジトリの **Settings → Pages → Build and deployment → Source** を **GitHub Actions** に変更する。  
   - `main`（または `master`）へ `push` すると `.github/workflows/deploy-pages.yml` が走り、CI 上で CSV からビルドして **Pages に公開**します。  
   - この場合、`.gitignore` により **`q/` と `sitemap.xml` はリポジトリに含めなくてよい**です（未追跡のままローカル確認用に生成するだけでよい）。  
   - **すでに `q/` をコミット済みの場合**は、次で追跡から外せます。  
     `git rm -r --cached q sitemap.xml` のあとコミット（ローカルの `q/` は残る）。

4. **ZIP にまとめて別サービスへ**  
   手元で `public_site` を作ったうえで、フォルダを ZIP に固めてアップロード（1ファイル）にすると、ファイル数制限のある画面でも扱いやすいことがあります。

## GitHub Pages（本番 `https://eisei2shu-master.jp/`）

### パターン A: GitHub Actions（`q/` を Git に載せない）

1. **Settings → Pages → Source** を **GitHub Actions** にする。  
2. `main` に push するとワークフローが `csv_to_eisei2_master` と `build_question_pages` を実行し、`public_site/` を Pages に載せる。  
3. DNS・`CNAME` は従来どおり。

### パターン B: ブランチのルートから配信（従来どおり）

1. **Settings → Pages → Source** を **Deploy from a branch**（例: `main` の `/ (root)`）にする。  
2. この場合は **`q/` と `sitemap.xml` をコミットに含める必要がある**ため、`.gitignore` の該当行（`/q/` と `/sitemap.xml`）を削除してから `git add q sitemap.xml` する。  
3. 公開は **`git push`** で行う（ブラウザの一括アップロードは非推奨）。

上記のどちらでも使える共通手順:

1. リポジトリ直下の **`CNAME`**（`eisei2shu-master.jp`）によりカスタムドメインを指定できる。DNS はドメイン側で GitHub の案内どおり **A / CNAME レコード**を設定する。  
2. ルートの **`robots.txt`** の `Sitemap` はビルドで **`https://eisei2shu-master.jp/sitemap.xml`** に更新される。Search Console にも同じ URL を登録するとよい。  
3. 静的問題の canonical / sitemap を再生成するときは  
   `python3 tools/build_question_pages.py --base-url https://eisei2shu-master.jp`  
   （サブパス公開にしない限り `--site-prefix` は不要）

## 注意

- 問題文は **学習用のサンプル** です。本番の出題・解答・法令の最新状況は **厚生労働省・安全衛生技術試験協会** 等の公式情報で確認してください。
- `index.html` 内の **Supabase URL/キー** は元テンプレのままです。本番運用では必ず **自プロジェクトのキー** に差し替え、RLS を設定してください。
- 試験日バナーは **例示日（2026-09-01）** です。受験予定に合わせて `index.html` 内のバナー文言とカウント用スクリプトを修正してください。
