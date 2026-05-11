# -*- coding: utf-8 -*-
"""Clone Desktop/index.html into this folder with 第二種衛生管理者向けパッチ。"""
import re
from pathlib import Path

SRC = Path("/Users/otedaiki/Desktop/index.html")
DST = Path(__file__).parent / "index.html"

NEW_ORIG_HTML = r'''      <div id="orig-category-area">
        <div class="orig-cat-section">
          <div class="orig-cat-header" onclick="toggleOrigCat('law')" role="button" tabindex="0" aria-expanded="false">
            <svg class="orig-cat-chevron" id="orig-chev-law" viewBox="0 0 16 16" aria-hidden="true"><path d="M6 4l4 4-4 4" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span class="orig-cat-label">関係法令</span>
            <span class="orig-cat-count" id="orig-cnt-law"></span>
            <button type="button" class="orig-cat-sel-all" id="orig-catbtn-law" onclick="event.stopPropagation();toggleAllOrigUnits('law')">一括選択</button>
          </div>
          <div class="orig-unit-grid closed" id="orig-units-law">
            <button class="orig-unit-btn" onclick="toggleOrigUnit('h_rouan')">労働安全衛生法の体系<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('h_kijun')">労働衛生基準則<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('h_eiseiti')">衛生管理者・委員会<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('h_tokkan')">化学物質・特化則<span class="orig-unit-n"></span></button>
          </div>
        </div>
        <div class="orig-cat-section">
          <div class="orig-cat-header" onclick="toggleOrigCat('rights')" role="button" tabindex="0" aria-expanded="false">
            <svg class="orig-cat-chevron" id="orig-chev-rights" viewBox="0 0 16 16" aria-hidden="true"><path d="M6 4l4 4-4 4" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span class="orig-cat-label">労働衛生</span>
            <span class="orig-cat-count" id="orig-cnt-rights"></span>
            <button type="button" class="orig-cat-sel-all" id="orig-catbtn-rights" onclick="event.stopPropagation();toggleAllOrigUnits('rights')">一括選択</button>
          </div>
          <div class="orig-unit-grid closed" id="orig-units-rights">
            <button class="orig-unit-btn" onclick="toggleOrigUnit('g_routai')">健康障害・作業管理の考え方<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('g_workenv')">作業環境管理の体系<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('g_noise')">騒音・振動<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('g_heat')">暑熱・寒冷<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('e_indoor')">換気・空調・給排水<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('e_dust')">粉じん・じんあい<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('e_rad')">放射線<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('e_met')">作業環境測定<span class="orig-unit-n"></span></button>
          </div>
        </div>
        <div class="orig-cat-section">
          <div class="orig-cat-header" onclick="toggleOrigCat('limit')" role="button" tabindex="0" aria-expanded="false">
            <svg class="orig-cat-chevron" id="orig-chev-limit" viewBox="0 0 16 16" aria-hidden="true"><path d="M6 4l4 4-4 4" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span class="orig-cat-label">労働生理</span>
            <span class="orig-cat-count" id="orig-cnt-limit"></span>
            <button type="button" class="orig-cat-sel-all" id="orig-catbtn-limit" onclick="event.stopPropagation();toggleAllOrigUnits('limit')">一括選択</button>
          </div>
          <div class="orig-unit-grid closed" id="orig-units-limit">
            <button class="orig-unit-btn" onclick="toggleOrigUnit('c_bio')">労働生理学<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('c_anatomy')">人体の解剖生理<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('c_chem')">衛生化学<span class="orig-unit-n"></span></button>
            <button class="orig-unit-btn" onclick="toggleOrigUnit('c_phys')">衛生物理学<span class="orig-unit-n"></span></button>
          </div>
        </div>
      </div>'''

NEW_ORIG_UNITS_JS = """const ORIG_UNITS = {
  rights:[
    {id:'g_routai',label:'健康障害・作業管理の考え方'},
    {id:'g_workenv',label:'作業環境管理の体系'},
    {id:'g_noise',label:'騒音・振動'},
    {id:'g_heat',label:'暑熱・寒冷'},
    {id:'e_indoor',label:'換気・空調・給排水'},
    {id:'e_dust',label:'粉じん・じんあい'},
    {id:'e_rad',label:'放射線'},
    {id:'e_met',label:'作業環境測定'},
  ],
  law:[
    {id:'h_rouan',label:'労働安全衛生法の体系'},
    {id:'h_kijun',label:'労働衛生基準則'},
    {id:'h_eiseiti',label:'衛生管理者・委員会'},
    {id:'h_tokkan',label:'化学物質・特化則'},
  ],
  limit:[
    {id:'c_bio',label:'労働生理学'},
    {id:'c_anatomy',label:'人体の解剖生理'},
    {id:'c_chem',label:'衛生化学'},
    {id:'c_phys',label:'衛生物理学'},
  ],
};
const ORIG_FIELD_LABELS = {law:'関係法令', rights:'労働衛生', limit:'労働生理'};
const ORIG_FIELD_COLORS = {law:'#1e4a8a', rights:'#1a5f4a', limit:'#8a5a1e'};
"""

NEW_MOCK_BLOCK = """// ===== MOCK EXAM PATTERNS（サンプル年度のみ） =====
const MOCK_PATTERNS = [
  {id:1, title:'模試 第1回', subtitle:'2023〜2024年サンプル問題から16問',
   desc:'デモ収録の過去問形式データから出題します。',
   years:[2023,2024]},
  {id:2, title:'模試 第2回', subtitle:'2023〜2024年サンプル 16問',
   desc:'同じ年度プールから別ランダムで出題（デモ）。',
   years:[2023,2024]},
];
const MOCK_DIST = {law:5, rights:6, limit:5};"""

def main():
    s = SRC.read_text(encoding="utf-8")

    # 外部データ
    s = s.replace('<script src="takken-master-data.js"></script>',
                  '<script src="eisei2-master-data.js"></script>')
    s = s.replace('<script src="takken-data-glossary.js"></script>',
                  '<script src="eisei2-data-glossary.js"></script>')
    s = s.replace('<script src="takken-data-original.js"></script>',
                  '<script src="eisei2-data-original.js"></script>')
    s = s.replace("loaded via takken-master-data.js", "loaded via eisei2-master-data.js")
    s = s.replace("takken-data-glossary.js , takken-data-original.js",
                  "eisei2-data-glossary.js , eisei2-data-original.js")

    # localStorage
    s = s.replace("'takken_v3'", "'eisei2kanri_v1'")
    s = s.replace("'takken_srs_v1'", "'eisei2kanri_srs_v1'")
    s = s.replace("'mock_bests'", "'eisei2_mock_bests'")

    # ドメイン・共有（本番）
    s = s.replace("https://takken-master.jp", "https://eisei2shu-master.jp")
    s = s.replace("takken-master-", "eisei2-master-")

    # Google Analytics 削除（デモ）
    s = re.sub(
        r"<!-- Google tag \(gtag\.js\) -->[\s\S]*?</script>\s*",
        "<!-- GA: 本番用の測定IDをここに -->\n",
        s,
        count=1,
    )

    # フィールド表示名マップ（複数箇所）
    old_map = "{rights:'権利関係',law:'宅建業法',limit:'法令制限',tax:'税・その他'}"
    new_map = "{law:'関係法令',rights:'労働衛生',limit:'労働生理'}"
    s = s.replace(old_map, new_map)

    # ORIG ブロック（JS）
    s = re.sub(
        r"const ORIG_UNITS = \{[\s\S]*?\n\};\nconst ORIG_FIELD_LABELS = \{[\s\S]*?\};\nconst ORIG_FIELD_COLORS = \{[\s\S]*?\};",
        NEW_ORIG_UNITS_JS,
        s,
        count=1,
    )

    # MOCK（宅建テンプレート／既存二衛ビルドの両方に対応）
    pat_takken = r"// ===== MOCK EXAM PATTERNS \(過去問から本試験配分で出題\) =====[\s\S]*?// 宅建本試験：[^\n]+\nconst MOCK_PATTERNS = \[[\s\S]*?\];\nconst MOCK_DIST = \{[^}]+\};"
    pat_eisei = r"// ===== MOCK EXAM PATTERNS（[^\n]*）\s*\nconst MOCK_PATTERNS = \[[\s\S]*?\];\nconst MOCK_DIST = \{[^}]+\};"
    if re.search(pat_takken, s):
        s = re.sub(pat_takken, NEW_MOCK_BLOCK, s, count=1)
    elif re.search(pat_eisei, s):
        s = re.sub(pat_eisei, NEW_MOCK_BLOCK, s, count=1)
    else:
        raise SystemExit("MOCK block not found")

    # 模試カードの表示タグ
    s = s.replace(
        '<span class="mock-tag">50問</span>\n        <span class="mock-tag">120分</span>\n        <span class="mock-tag">権利14 業法20 制限8 税8</span>',
        '<span class="mock-tag">16問</span>\n        <span class="mock-tag">180分目安</span>\n        <span class="mock-tag">関係法令5・労働衛生6・労働生理5</span>',
    )

    # オリジナル問題ページの HTML ブロック
    m = re.search(
        r'<div id="orig-category-area">[\s\S]*?</div>\s*\n\s*</div>\s*\n\s*\n\s*<!-- MOCK EXAM SELECT -->',
        s,
    )
    if not m:
        raise SystemExit("orig-category-area block not found")
    s = s[: m.start()] + NEW_ORIG_HTML + "\n\n    <!-- MOCK EXAM SELECT -->" + s[m.end() :]

    # CAT_HINT・プレースホルダ（グローバル置換で壊れないよう先に）
    s = re.sub(
        r"const CAT_HINT=\{[\s\S]*?\n  \};",
        """const CAT_HINT={
    rights:'労働衛生：リスク評価、温熱・騒音振動、局所排気・換気・捕集分析・測定と化学物質管理の考え方を整理します。',
    law:'関係法令：選任・委員会・基準・測定記録・健康診断・特化則の「いつ誰が何を」で整理します。',
    limit:'労働生理：人体の調節、有害因子の作用、放射線生物学、振動などの用語を定義レベルで押さえます。',
    exam:'学習の進め方・肢の読み方。長文は主語（誰の義務か）と数値条件をマークすると速くなります。'
  };""",
        s,
        count=1,
    )
    s = s.replace(
        "const PLACEHOLDER_SNIPPET='宅建試験の頻出論点です。定義・比較表・具体例を公開サイトの解説記事で詳しく確認できます。';",
        "const PLACEHOLDER_SNIPPET='試験の頻出論点です。定義・比較表・具体例を公開サイトの解説記事で詳しく確認できます。';",
    )

    # ブランド一括（「2026年宅建試験」など複合語を先に）
    reps = [
        ("宅建マスター", "二衛マスター"),
        ("2026年宅建試験まで", "次回試験予定日まで（例）"),
        ("宅建試験", "第二種衛生管理者試験"),
        ("宅建士試験", "第二種衛生管理者試験"),
        ("宅建合格", "合格"),
        ("宅地建物取引士", "第二種衛生管理者"),
        ("宅建（宅地建物取引士）", "第二種衛生管理者"),
        ("demo@takken.app", "demo@eisei2.example"),
        ("（2026年10月18日）", "（2026年9月1日・要公式確認）"),
        ("不動産適正取引推進機構（RETIO）", "厚生労働省・安全衛生技術試験協会の公式情報"),
        ("https://www.retio.or.jp", "https://www.mhlw.go.jp/"),
        ("全1000問", "デモ収録"),
        ("10年以上掲載", "2023〜2024サンプル"),
        ("1,000問以上掲載", "レベル別サンプル"),
        ("宅建の重要用語", "試験で出やすい用語"),
        ("宅建業法", "労働衛生関係法令"),
        ("権利関係", "労働衛生一般"),
        ("法令上の制限", "労働生理"),
        ("税・その他", "労働衛生（測定・換気等）"),
    ]
    for a, b in reps:
        s = s.replace(a, b)

    # 略称「宅建」が残る箇所の後処理（meta・静的HTML・正規表現など）
    tail_reps = [
        ("raw=raw.replace(/^.{0,80}?(第二種衛生管理者試験|宅建士\\s*試験|試験\\s*番号)/,'');",
         "raw=raw.replace(/^.{0,80}?(第二種衛生管理者試験|試験\\s*番号|令和|平成)/,'');"),
        ("（宅建）", ""),
        ("const SHARE_TWITTER_HASHTAGS = '宅建,試験勉強,二衛マスター'", "const SHARE_TWITTER_HASHTAGS = '衛生管理者,第二種衛生管理者,二衛マスター'"),
        ("宅建（第二種衛生管理者）", "第二種衛生管理者"),
        ("宅建,第二種衛生管理者", "第二種衛生管理者,衛生管理者試験"),
        ("宅建過去問", "試験演習"),
        ("宅建学習", "資格学習"),
        ("宅建重要用語", "重要用語"),
        ("宅建勉強の", "学習の"),
        ("宅建勉強", "試験勉強"),
        ("宅建,宅建勉強,二衛マスター", "衛生管理者,第二種衛生管理者,二衛マスター"),
        ("宅建の頻出分野", "試験の頻出分野"),
        ("宅建士証を手にした", "合格を手にした"),
        ("宅建士が", "衛生管理者が"),
        ("宅建士", "衛生管理者"),
        ("宅建業者", "事業者"),
        ("宅建は繰り返し", "本試験は繰り返し"),
        ("宅建問題", "演習問題"),
        ("（定数 GLOSSARY_DATA は takken-data-glossary.js）", "（定数 GLOSSARY_DATA は eisei2-data-glossary.js）"),
    ]
    for a, b in tail_reps:
        s = s.replace(a, b)

    # ロゴ短名（「宅建」2文字が残る箇所）
    s = s.replace(">宅建<", ">二衛<")

    # 試験日カウント
    s = s.replace("new Date('2026-10-18T00:00:00+09:00')", "new Date('2026-09-01T00:00:00+09:00')")

    s = s.replace(
        "||'宅建の主要科目にまたがる用語です。",
        "||'主要科目にまたがる用語です。",
    )

    # X 投稿文の残り「宅建」
    s = s.replace("宅建マスターで一問一答", "二衛マスターで一問一答")
    s = s.replace("宅建合格を目指して", "第二種衛生管理者合格を目指して")

    # 模試タイマー 180分（該当箇所のみ置換しすぎないよう1回）
    s = s.replace("mockState.totalSec = 120*60", "mockState.totalSec = 180*60", 1)

    # 音声学習（audio）を省略 — ナビ・ページ・PAGE_TITLES・gotoPage アクティブ判定
    s = re.sub(
        r"\n\s*<a class=\"topnav-link\" id=\"tnav-audio\"[\s\S]*?</a>",
        "",
        s,
        count=1,
    )
    s = re.sub(
        r"\n\s*<a class=\"mobile-nav-item\" id=\"mnav-audio\"[\s\S]*?</a>",
        "",
        s,
        count=1,
    )
    s = re.sub(
        r"\n\n    <!-- AUDIO PAGE -->[\s\S]*?(?=\n  </main>)",
        "\n\n",
        s,
        count=1,
    )
    s = s.replace(",'audio':'音声学習'", "")
    s = s.replace("      'audio':    id==='audio',\n", "")

    # X ハッシュタグ・SEO 表記の残り修正・模試ページ（再生成時も維持）
    s = s.replace(
        "const SHARE_TWITTER_HASHTAGS = '宅建,試験勉強,二衛マスター'",
        "const SHARE_TWITTER_HASHTAGS = '衛生管理者,第二種衛生管理者,二衛マスター'",
    )
    s = s.replace("衛生化・生理解剖・税その他）", "衛生化・生理解剖・衛生工学等）")
    s = s.replace("衛生化・生理解剖・税その他に対応。", "衛生化・生理解剖・衛生工学等に対応。")
    s = s.replace("衛生化・生理解剖・税その他の単元別200問", "衛生化・生理解剖・衛生工学等の単元別200問")
    s = re.sub(
        r"    <!-- MOCK EXAM SELECT -->[\s\S]*?(?=    <!-- MOCK SCORE -->)",
        """    <!-- MOCK EXAM SELECT -->
    <div class="page" id="page-mock">
      <nav class="breadcrumb" aria-label="パンくずリスト">
        <ol class="breadcrumb-list">
          <li class="breadcrumb-item"><a href="/" onclick="event.preventDefault();gotoPage('quiz-start')">二衛マスター</a></li>
          <li class="breadcrumb-item breadcrumb-current" aria-current="page">オリジナル模試</li>
        </ol>
      </nav>
      <h2 class="page-title">オリジナル模試</h2>
      <div class="page-sub">サンプル年度の演習問題から、分野別配分で16問（デモ）</div>
      <div class="mock-grid" id="mock-grid"></div>
    </div>

""",
        s,
        count=1,
    )

    DST.write_text(s, encoding="utf-8")
    print("Wrote", DST, "chars", len(s))


if __name__ == "__main__":
    main()
