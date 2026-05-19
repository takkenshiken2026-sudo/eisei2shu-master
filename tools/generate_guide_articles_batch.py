#!/usr/bin/env python3
"""試験ガイド記事HTMLをテンプレートから生成する（バッチ追加用）。"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTICLES_DIR = REPO / "articles"
TEMPLATE = ARTICLES_DIR / "ikkagetsu-goukaku.html"
DATE = "2026-05-19"
SITE = "https://eisei2shu-master.jp"


def load_parts() -> tuple[str, str, str]:
    text = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"(<style>.*?</style>)", text, re.DOTALL)
    if not m:
        raise RuntimeError("style block not found")
    style = m.group(1)
    h0 = text.index('<header class="site-header">')
    h1 = text.index('<h1 class="article-title">')
    header = text[h0:h1]
    t0 = text.index("</article>")
    tail = text[t0:]
    return style, header, tail


def related_box(links: list[tuple[str, str]]) -> str:
    if not links:
        return ""
    items = "\n".join(
        f'    <a href="{html.escape(href, quote=True)}" class="related-link">'
        f"{html.escape(label)}</a>"
        for href, label in links
    )
    return (
        '\n<div class="related-box">\n'
        '  <div class="related-box-title">関連するガイド・用語</div>\n'
        '  <div class="related-links">\n'
        f"{items}\n"
        "  </div>\n"
        "</div>\n"
    )


def faq_json_ld(faqs: list[tuple[str, str]]) -> str:
    if not faqs:
        return ""
    entities = []
    for q, a in faqs:
        entities.append(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
        )
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}
    return (
        '\n<script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n</script>\n"
    )


def render(article: dict, style: str, header: str, tail: str) -> str:
    slug = article["slug"]
    title = article["title"]
    desc = article["description"]
    short = article.get("breadcrumb") or title.split("【")[0].strip()
    url = f"{SITE}/articles/{slug}.html"
    body = article["body"].strip()
    related = related_box(article.get("related", []))
    faq_ld = faq_json_ld(article.get("faqs", []))

    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{SITE}/#website",
                "url": f"{SITE}/",
                "name": "二衛マスター",
                "description": "第二種衛生管理者試験の無料学習プラットフォーム",
                "inLanguage": "ja",
            },
            {
                "@type": "Article",
                "@id": f"{url}#article",
                "headline": title,
                "description": desc,
                "dateModified": DATE,
                "inLanguage": "ja",
                "isPartOf": {"@id": f"{SITE}/#website"},
                "publisher": {
                    "@type": "Organization",
                    "name": "二衛マスター",
                    "url": f"{SITE}/",
                },
            },
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "トップ",
                        "item": f"{SITE}/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": short,
                        "item": url,
                    },
                ],
            },
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">

<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:locale" content="ja_JP">
<meta property="og:site_name" content="二衛マスター">

<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">

<script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=2)}
</script>
{faq_ld}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700&display=swap" rel="stylesheet">

{style}
</head>
<body>

{header}
  <nav class="breadcrumb" aria-label="パンくず">
    <a href="/">トップ</a>
    <span class="breadcrumb-sep">›</span>
    <a href="/articles/">試験・学習ガイド</a>
    <span class="breadcrumb-sep">›</span>
    <span>{html.escape(short)}</span>
  </nav>

  <div class="article-meta">
    <span class="meta-category"></span>
    <span class="meta-updated">更新日：{DATE}</span>
  </div>

  <h1 class="article-title">{html.escape(title)}</h1>

  <article class="article-body">
{body}
{related}
  </article>

{tail}
"""


ARTICLES: list[dict] = [
    {
        "slug": "3kagetsu-goukaku",
        "title": "第二種衛生管理者の3ヶ月勉強計画【週別ロードマップ】",
        "breadcrumb": "3ヶ月勉強計画",
        "description": "第二種衛生管理者試験を3ヶ月で受けるための週別計画。1日1〜1.5時間・週5日で約90時間。基礎→演習→過去問の流れを整理します。",
        "related": [
            ("/articles/dokugaku-guide.html", "独学合格ガイド"),
            ("/articles/ikkagetsu-goukaku.html", "1ヶ月勉強計画"),
            ("/articles/benkyou-jikan.html", "勉強時間の目安"),
        ],
        "faqs": [
            (
                "3ヶ月で合格するのに必要な勉強時間は？",
                "1日1〜1.5時間・週5日で約90時間が目安です。労働生理が苦手な場合は早めに並行学習を始めます。",
            ),
        ],
        "body": """
    <p>試験日の3ヶ月前から始める標準プランです。1日1〜1.5時間・週5日（合計おおよそ90時間）を想定しています。</p>
<hr />
<h2>3ヶ月プランの全体像</h2>
<table>
<thead><tr><th>期間</th><th>重点</th><th>目標</th></tr></thead>
<tbody>
<tr><td><strong>1〜4週目</strong></td><td>テキスト通読・数値整理</td><td>3科目を一通り読み、重要数値に印をつける</td></tr>
<tr><td><strong>5〜8週目</strong></td><td>科目別演習</td><td>分野ごとに理解度チェック、弱点を特定</td></tr>
<tr><td><strong>9〜11週目</strong></td><td>過去問</td><td>直近3〜5回分を解説まで読み込む</td></tr>
<tr><td><strong>12週目</strong></td><td>直前調整</td><td>数値・誤りやすい条件の最終確認</td></tr>
</tbody>
</table>
<hr />
<h2>科目別の時間配分（目安）</h2>
<table>
<thead><tr><th>科目</th><th>割合</th><th>ポイント</th></tr></thead>
<tbody>
<tr><td>関係法令</td><td>40%</td><td>選任人数・健診頻度・保存期間を表にまとめる</td></tr>
<tr><td>労働衛生</td><td>35%</td><td>局所排気・測定・管理区分を図で整理</td></tr>
<tr><td>労働生理</td><td>25%</td><td>毎日少しずつ。後回しにしない</td></tr>
</tbody>
</table>
<p>→ <a href="/articles/6kagetsu-keikaku.html">6ヶ月プランはこちら</a> ／ <a href="/terms/sogo-matome-suuchi.html">数値総まとめ</a></p>
""",
    },
    {
        "slug": "6kagetsu-keikaku",
        "title": "第二種衛生管理者の6ヶ月勉強計画【働きながら受験】",
        "breadcrumb": "6ヶ月勉強計画",
        "description": "仕事と両立しながら第二種衛生管理者試験に挑む6ヶ月計画。週10〜12時間・復習サイクルを含めた学習の進め方を解説します。",
        "related": [
            ("/articles/3kagetsu-goukaku.html", "3ヶ月勉強計画"),
            ("/articles/dokugaku-guide.html", "独学合格ガイド"),
            ("/articles/tsushin-kouza-vs-dokugaku.html", "通信講座と独学の比較"),
        ],
        "body": """
    <p>週10〜12時間（1日30〜40分＋週末にまとめて学習）を想定した、働きながら受験する方向けの計画です。</p>
<hr />
<h2>6ヶ月の段階的な進め方</h2>
<table>
<thead><tr><th>月</th><th>やること</th></tr></thead>
<tbody>
<tr><td>1〜2ヶ月目</td><td>関係法令を中心にテキスト通読。数値は自分の一覧表を作成</td></tr>
<tr><td>3〜4ヶ月目</td><td>労働衛生・労働生理を追加。用語解説で理解を補強</td></tr>
<tr><td>5ヶ月目</td><td>過去問を解き、解説を熟読</td></tr>
<tr><td>6ヶ月目</td><td>弱点科目の反復・直前は新規インプットを控える</td></tr>
</tbody>
</table>
<hr />
<h2>復習を組み込むコツ</h2>
<ul>
<li><strong>週末15分</strong>：その週に学んだ数値だけ声に出して確認</li>
<li><strong>月1回</strong>：間違えた問題だけ再挑戦（→ <a href="/articles/bookmark-fukushu.html">間違え問題の復習サイクル</a>）</li>
<li><strong>試験2ヶ月前</strong>：申込・会場確認まで完了させる</li>
</ul>
""",
    },
    {
        "slug": "saijuken-taisaku",
        "title": "第二種衛生管理者の再受験対策【不合格からの立て直し】",
        "breadcrumb": "再受験対策",
        "description": "第二種衛生管理者試験に不合格だった場合の再受験対策。足切り科目の特定・勉強法の見直し・スケジュールの立て方を整理します。",
        "related": [
            ("/articles/nankaimo-ochiru.html", "合格ラインと落ちる理由"),
            ("/articles/goukakuritsu.html", "合格率・難易度"),
            ("/articles/nankaisei.html", "何問正解で合格か"),
        ],
        "faqs": [
            (
                "再受験はいつから申し込めますか？",
                "試験日程・申込期間は安全衛生技術試験協会の公式案内で確認してください。本記事は学習の立て直し方に焦点を当てています。",
            ),
        ],
        "body": """
    <p>不合格後は「何が足りなかったか」を科目別に切り分けることが再受験成功の第一歩です。</p>
<hr />
<h2>まず確認すること</h2>
<table>
<thead><tr><th>確認項目</th><th>対策</th></tr></thead>
<tbody>
<tr><td>足切り科目があるか</td><td>最も得点が低い科目を優先的に補強</td></tr>
<tr><td>数値問題の正答率</td><td><a href="/articles/suuchi-anki-list.html">数値暗記リスト</a>で再整理</td></tr>
<tr><td>過去問の解説を読んだか</td><td>正解問題も含め解説を音読する</td></tr>
<tr><td>勉強時間が足りたか</td><td>3ヶ月以上の計画に切り替える</td></tr>
</tbody>
</table>
<hr />
<h2>再受験2ヶ月プラン（例）</h2>
<ol>
<li><strong>1〜3週目</strong>：足切り科目のテキストを再読＋演習</li>
<li><strong>4〜6週目</strong>：過去問を本番形式で2回分</li>
<li><strong>7〜8週目</strong>：間違え問題のみ反復、数値の最終確認</li>
</ol>
""",
    },
    {
        "slug": "ichimon-ittou",
        "title": "第二種衛生管理者の1問1答演習のやり方【暗記定着】",
        "breadcrumb": "1問1答演習",
        "description": "第二種衛生管理者試験向けに1問1答形式で復習する方法。アプリ・問題集・過去問との組み合わせ方を解説します。",
        "related": [
            ("/articles/kakomon-nannennbun.html", "過去問は何年分"),
            ("/articles/osusume-app.html", "おすすめ学習アプリ"),
            ("/articles/shutsudai-keiko.html", "出題傾向の把握"),
        ],
        "body": """
    <p>1問1答は隙間時間の定着に有効ですが、解説を読まない「なぞりがち学習」には注意が必要です。</p>
<hr />
<h2>効果的な1問1答の使い方</h2>
<table>
<thead><tr><th>ステップ</th><th>内容</th></tr></thead>
<tbody>
<tr><td>1</td><td>テキストで該当分野を読んでから問題に取り組む</td></tr>
<tr><td>2</td><td>不正解は理由を1行でメモ（なぜ他の肢が誤りか）</td></tr>
<tr><td>3</td><td>24時間後・1週間後に同じ問題だけ再挑戦</td></tr>
</tbody>
</table>
<hr />
<h2>向いている・向いていない題材</h2>
<ul>
<li><strong>向いている</strong>：数値、保存期間、選任人数、用語定義</li>
<li><strong>向いていない</strong>：複数条件の組み合わせ問題（過去問形式で練習）</li>
</ul>
""",
    },
    {
        "slug": "jikan-haibun",
        "title": "第二種衛生管理者試験の時間配分【30問・3時間の進め方】",
        "breadcrumb": "試験の時間配分",
        "description": "第二種衛生管理者試験（30問・180分）の時間配分の目安。科目ごとの優先順位・見直し時間・詰まったときの対処を整理します。",
        "related": [
            ("/articles/goukaku-kijun.html", "合格基準・足切り"),
            ("/articles/nankaisei.html", "合格ラインの目安"),
            ("/articles/shiken-kamoku.html", "試験科目と出題範囲"),
        ],
        "body": """
    <p>30問・180分は1問あたり平均6分です。最初から全問に同じ時間をかけると後半が不足しやすいため、配分を決めておきます。</p>
<hr />
<h2>おすすめの時間配分</h2>
<table>
<thead><tr><th>フェーズ</th><th>時間</th><th>内容</th></tr></thead>
<tbody>
<tr><td>第1周</td><td>120分</td><td>得意科目から解く。1問4〜5分を目安</td></tr>
<tr><td>第2周</td><td>45分</td><td>見直し・迷った問題・計算問題</td></tr>
<tr><td>予備</td><td>15分</td><td>マークミス確認・解答欄の記入漏れ</td></tr>
</tbody>
</table>
<hr />
<h2>科目別の進め方</h2>
<ul>
<li><strong>関係法令</strong>：数値・条件の問題は早めに処理</li>
<li><strong>労働衛生</strong>：図表問題は読み込みに時間がかかるため中盤に配置</li>
<li><strong>労働生理</strong>：知識問題は直感で、不明は印をつけて後回し</li>
</ul>
<p>→ <a href="/articles/shiken-tojitsu-nagare.html">試験当日の流れ</a></p>
""",
    },
    {
        "slug": "shiken-tojitsu-nagare",
        "title": "第二種衛生管理者試験当日の流れ【受付から退場まで】",
        "breadcrumb": "試験当日の流れ",
        "description": "第二種衛生管理者試験当日の流れと注意点。受付・着席・休憩・提出までの手順と、当日に確認すべき持ち物を整理します。",
        "related": [
            ("/articles/shiken-tojitsu-mochimono.html", "当日の持ち物"),
            ("/articles/shiken-kaijo.html", "試験会場・アクセス"),
            ("/articles/jikan-haibun.html", "時間配分の目安"),
        ],
        "body": """
    <p>会場によって細部は異なります。最新の案内は受験票・公式情報で必ず確認してください。</p>
<hr />
<h2>当日の一般的な流れ</h2>
<table>
<thead><tr><th>段階</th><th>内容</th></tr></thead>
<tbody>
<tr><td>到着</td><td>開始30〜60分前を目安に会場へ。交通遅延を想定</td></tr>
<tr><td>受付</td><td>受験票・身分証明書を提示</td></tr>
<tr><td>着席</td><td>指定席・解答用紙の記入事項を確認</td></tr>
<tr><td>試験</td><td>開始合図後に解答。途中退出の可否は案内に従う</td></tr>
<tr><td>終了</td><td>提出・退場。結果は後日発表</td></tr>
</tbody>
</table>
<blockquote><p><strong>注意</strong>：携帯電話・スマートウォッチ等の持ち込み制限は会場案内に従ってください。</p></blockquote>
""",
    },
    {
        "slug": "kanri-kubun-oboekata",
        "title": "作業環境管理区分の覚え方【第1〜第3管理・措置A/B】",
        "breadcrumb": "管理区分の覚え方",
        "description": "第二種衛生管理者試験で頻出の作業環境管理区分（第1〜第3管理、措置A・B）の覚え方。測定結果から区分を判断する流れを整理します。",
        "related": [
            ("/articles/sagyo-kankyo-kanri-flow.html", "作業環境管理の流れ"),
            ("/articles/sagyo-kankyohyoka-kanri.html", "作業環境評価と管理"),
            ("/terms/kanri-kubun-dai1.html", "第1管理（用語）"),
        ],
        "body": """
    <p>管理区分は「測定→評価→区分→措置→再評価」の流れで理解すると、単語暗記より応用に強くなります。</p>
<hr />
<h2>覚える順序</h2>
<ol>
<li>許容濃度・管理濃度の意味（→ <a href="/terms/kyoyo-nodo.html">許容濃度</a>、<a href="/terms/kanri-nodo.html">管理濃度</a>）</li>
<li>第3管理（良好）→ 第2管理 → 第1管理（要改善）のイメージ</li>
<li>措置A・措置Bがいつ必要かを表で整理</li>
</ol>
<hr />
<h2>試験での誤りパターン</h2>
<ul>
<li>「第1管理＝最も良い環境」→ <strong>誤り</strong>（改善が必要な側）</li>
<li>「措置は1回で終わり」→ 再測定・再評価が必要な場面がある</li>
</ul>
<p>→ <a href="/terms/sochi-a.html">措置A</a> ／ <a href="/terms/sochi-b.html">措置B</a></p>
""",
    },
    {
        "slug": "sagyo-shunin-ichiran",
        "title": "作業主任者の種類と資格一覧【第二種衛生管理者試験】",
        "breadcrumb": "作業主任者一覧",
        "description": "有機溶剤・特定化学物質・鉛・酸素欠乏・石綿など、作業主任者の種類と必要な技能講習・資格を一覧で整理。試験の頻出テーマです。",
        "related": [
            ("/terms/sagyoshunin-sha.html", "作業主任者（用語）"),
            ("/articles/tokubetsu-kyoiku-jugyomae.html", "特別教育の実施時期"),
            ("/articles/yuki-yozai-kubun-gimu.html", "有機溶剤の区分と義務"),
        ],
        "body": """
    <p>作業主任者は「どの作業で」「どの規則に基づき」選任されるかをセットで覚えます。</p>
<hr />
<h2>代表する作業主任者</h2>
<table>
<thead><tr><th>作業主任者</th><th>関連規則・テーマ</th></tr></thead>
<tbody>
<tr><td>有機溶剤作業主任者</td><td><a href="/terms/yuki-yozai-sagyo-shunin.html">有機溶剤作業主任者</a></td></tr>
<tr><td>特定化学物質作業主任者</td><td><a href="/terms/tokutei-kagaku-sagyo-shunin.html">特定化学物質作業主任者</a></td></tr>
<tr><td>鉛作業主任者</td><td><a href="/terms/namari-sagyo-shunin.html">鉛作業主任者</a></td></tr>
<tr><td>酸素欠乏危険作業主任者</td><td><a href="/terms/sanso-kiken-sagyo-shunin.html">酸素欠乏危険作業主任者</a></td></tr>
</tbody>
</table>
<hr />
<h2>衛生管理者との違い</h2>
<p>作業主任者は<strong>特定作業の現場指揮</strong>、衛生管理者は<strong>事業場全体の衛生管理</strong>です。どちらか一方がいれば足りる、という整理は誤りになりやすい点に注意してください。</p>
""",
    },
    {
        "slug": "niji-kenko-shindan-guide",
        "title": "二次健康診断の流れと就業上の措置【事業者の対応】",
        "breadcrumb": "二次健康診断の流れ",
        "description": "一次健康診断後の二次健康診断の目的、実施時期、就業上の措置との関係を第二種衛生管理者試験向けに整理します。",
        "related": [
            ("/articles/kenko-shindan-jigo-tejun.html", "健康診断後の事後措置"),
            ("/articles/kenko-shindan-hindo.html", "健康診断の頻度"),
            ("/terms/niji-kenko-shindan.html", "二次健康診断（用語）"),
        ],
        "body": """
    <p>二次健康診断は、一次健診で所見があった場合などに実施する精密検査です。結果に応じた就業上の措置まで一連の流れで覚えます。</p>
<hr />
<h2>基本的な流れ</h2>
<table>
<thead><tr><th>段階</th><th>内容</th></tr></thead>
<tbody>
<tr><td>一次健康診断</td><td>定期・雇入時など</td></tr>
<tr><td>所見・通知</td><td>医師の意見、労働者への通知</td></tr>
<tr><td>二次健康診断</td><td>精密検査の実施</td></tr>
<tr><td>就業上の措置</td><td>就業禁止・配置転換など（→ <a href="/terms/shugyo-jo-sochi.html">就業上の措置</a>）</td></tr>
</tbody>
</table>
<blockquote><p>実施時期・通知期限などの数値は、受験前に公式情報・テキストで最新を確認してください。</p></blockquote>
""",
    },
    {
        "slug": "bookmark-fukushu",
        "title": "間違え問題の復習サイクル【過去問・一問一答の定着法】",
        "breadcrumb": "間違え問題の復習",
        "description": "第二種衛生管理者試験で間違えた問題を効率よく復習するサイクル。1日後・1週間後・1ヶ月後の反復と、ノートの作り方を解説します。",
        "related": [
            ("/articles/dokugaku-guide.html", "独学合格ガイド"),
            ("/articles/kakomon-nannennbun.html", "過去問は何年分"),
            ("/articles/ichimon-ittou.html", "1問1答演習"),
        ],
        "body": """
    <p>同じ問題を何度も間違える原因の多くは「解説を読んだつもり」になっていることです。思い出すタイミングをずらして復習します。</p>
<hr />
<h2>3段階復習サイクル</h2>
<table>
<thead><tr><th>タイミング</th><th>やること</th></tr></thead>
<tbody>
<tr><td><strong>当日</strong></td><td>誤り理由を1行メモ。正解の根拠を声に出す</td></tr>
<tr><td><strong>翌日</strong></td><td>印のついた問題だけ再解答（テキストは見ない）</td></tr>
<tr><td><strong>1週間後</strong></td><td>まだ間違う問題は関連用語記事を読む</td></tr>
</tbody>
</table>
<hr />
<h2>ノートより「問題集への印」が効率的</h2>
<p>転記に時間をかけすぎないよう、問題番号＋誤った理由（数値ミス／条文混同など）をコード化すると復習が速くなります。</p>
<p>→ 本サイトの<a href="/">過去問演習</a>と併用すると、間違えた問題を科目別に振り返れます。</p>
""",
    },
]


def main() -> None:
    style, header, tail = load_parts()
    created = 0
    for art in ARTICLES:
        out = ARTICLES_DIR / f"{art['slug']}.html"
        if out.exists():
            print(f"skip exists: {out.name}")
            continue
        out.write_text(render(art, style, header, tail), encoding="utf-8")
        created += 1
        print(f"created: {out.name}")

    idx_script = REPO / "tools" / "generate_articles_index.py"
    if created and idx_script.is_file():
        subprocess.run([sys.executable, str(idx_script)], check=True, cwd=REPO)

    print(f"done: {created} new articles ({len(list(ARTICLES_DIR.glob('*.html')))} html files total)")


if __name__ == "__main__":
    main()
