#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""学習導線（三角リンク）HTML 断片の生成。"""

from __future__ import annotations

import html

from learning_links_lib import (
    intent_links_for_category,
    intent_links_for_field,
    matome_for_category,
    matome_for_field,
    question_links_for_term,
    slug_display_name,
    term_href,
)


def _ul(links: list[tuple[str, str]]) -> str:
    if not links:
        return "<p class=\"term-learning-empty\">関連リンクを準備中です。</p>"
    items = "\n".join(
        f'    <li><a href="{html.escape(href)}">{html.escape(label)}</a></li>'
        for href, label in links
    )
    return f"<ul>\n{items}\n  </ul>"


def render_term_learning_hub(
    slug: str,
    category: str,
    related_questions_fm,
) -> str:
    matome_href, matome_label = matome_for_category(category)
    past_links = question_links_for_term(slug, related_questions_fm)
    intent_links = intent_links_for_category(category, limit=3)
    past_block = _ul(past_links) if past_links else (
        '<p class="term-learning-empty">'
        '<a href="/q/index.html">過去問一覧</a>から該当テーマの問題を探せます。'
        "</p>"
    )
    return f"""<section id="term-learning-path" class="term-info-box term-learning-hub">
  <h2>学習のつながり</h2>
  <p class="term-learning-intro">用語の理解 → 科目まとめ → 過去問演習の順で復習すると記憶が定着しやすくなります。</p>
  <h3 class="term-learning-subhead">科目まとめ</h3>
  <ul>
    <li><a href="{html.escape(matome_href)}">{html.escape(matome_label)}</a></li>
    <li><a href="/articles/index.html">試験・学習ガイド一覧</a></li>
  </ul>
  <h3 class="term-learning-subhead">関連する過去問</h3>
  {past_block}
  <h3 class="term-learning-subhead">検索意図ガイド</h3>
  {_ul(intent_links)}
</section>"""


def render_question_learning_hub(
    field: str,
    term_entries: list[tuple[str, str]],
    session_hub_href: str | None = None,
    session_hub_label: str | None = None,
) -> str:
    matome_href, matome_label = matome_for_field(field)
    term_links = [(term_href(s), name) for name, s in term_entries[:6]]
    intent_links = intent_links_for_field(field, limit=2)
    extra = ""
    if session_hub_href and session_hub_label:
        extra = (
            f'  <h3 class="term-learning-subhead">この開催回</h3>\n'
            f'  <ul><li><a href="{html.escape(session_hub_href)}">'
            f"{html.escape(session_hub_label)}</a></li></ul>\n"
        )
    return f"""<section class="q-block term-learning-hub" aria-labelledby="q-learn-h">
  <h2 id="q-learn-h" class="q-h2">学習のつながり</h2>
  <p class="term-learning-intro">解説を読んだあとは、下の<strong>関連用語</strong>（用語解説記事）と科目まとめで定着を確認しましょう。キーワードの意味は <a href="/terms/">用語解説一覧</a> からも探せます。</p>
{extra}  <h3 class="term-learning-subhead">関連用語</h3>
  {_ul(term_links)}
  <h3 class="term-learning-subhead">科目まとめ</h3>
  <ul>
    <li><a href="{html.escape(matome_href)}">{html.escape(matome_label)}</a></li>
    <li><a href="/terms/">用語解説一覧</a></li>
  </ul>
  <h3 class="term-learning-subhead">検索意図ガイド</h3>
  {_ul(intent_links)}
</section>"""


def render_session_hub_page_body(heading: str, question_sections_html: str) -> str:
    return f"""<p class="glos-static-intro q-index-intro"><strong>{html.escape(heading)}</strong>の過去問を科目別にまとめています。各問題から解説・関連用語へ進めます。</p>
<section class="term-learning-hub matome-learning-hub" aria-labelledby="sess-hub-learn">
  <h2 id="sess-hub-learn">学習のつながり</h2>
  <ul>
    <li><a href="/terms/">用語解説一覧</a></li>
    <li><a href="/articles/index.html">試験・学習ガイド一覧</a></li>
    <li><a href="/articles/dokugaku-guide.html">独学合格ガイド</a></li>
    <li><a href="/articles/nankaisei.html">合格ラインの整理</a></li>
  </ul>
</section>
{question_sections_html}"""


def render_session_hub_learning_intro(field: str) -> str:
    matome_href, matome_label = matome_for_field(field)
    intents = intent_links_for_field(field, limit=2)
    intent_ul = _ul(intents)
    return f"""<p class="glos-static-intro q-index-intro">この開催回の過去問は科目別に下記から選べます。あわせて <a href="{html.escape(matome_href)}">{html.escape(matome_label)}</a> と用語解説で復習すると理解が深まります。</p>
{intent_ul}"""


def render_matome_learning_hub(matome_filename: str, field: str) -> str:
    from learning_links_lib import MATOME_FEATURED_TERMS

    matome_href, matome_label = matome_for_field(field)
    slugs = MATOME_FEATURED_TERMS.get(matome_filename, [])
    term_links = [(term_href(s), slug_display_name(s)) for s in slugs]
    intent_links = intent_links_for_field(field, limit=3)
    return f"""<section class="term-learning-hub matome-learning-hub" aria-labelledby="matome-learn-h">
  <h2 id="matome-learn-h">学習のつながり</h2>
  <p class="term-learning-intro">まとめ記事で全体像を押さえたあと、用語解説と過去問で出題形式に慣れましょう。</p>
  <h3 class="term-learning-subhead">代表用語</h3>
  {_ul(term_links)}
  <h3 class="term-learning-subhead">過去問</h3>
  <ul>
    <li><a href="/q/index.html">過去問一覧（年度・科目別）</a></li>
    <li><a href="/">アプリで過去問演習</a></li>
  </ul>
  <h3 class="term-learning-subhead">検索意図ガイド</h3>
  {_ul(intent_links)}
</section>"""
