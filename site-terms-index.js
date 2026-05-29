/**
 * 用語集一覧 terms/index.html — 4セクション（用語解説 / 比較・整理表 / 数値・期限早見表 / よくある誤答）
 * 再生成: python3 tools/build_glossary_pages.py
 */
(() => {
  'use strict';

  document.documentElement.classList.add('js');

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const dataEl = document.getElementById('terms-index-data');
  const ITEMS = dataEl ? JSON.parse(dataEl.textContent || '[]') : [];

  const q = document.getElementById('terms-idx-q');
  const chips = $$('.terms-idx-chip[data-cat]');
  const hit = document.getElementById('terms-idx-hit');
  const empty = document.getElementById('terms-idx-empty');
  const toolbarReset = document.getElementById('terms-idx-reset');
  const clearBtn = document.getElementById('terms-idx-clear');
  const activeFilters = document.getElementById('terms-idx-active-filters');
  const toolbar = document.querySelector('.terms-index-tools');
  const topBtn = document.getElementById('terms-idx-top');
  const sectionBodies = $$('tbody[data-section]');
  const sectionHits = $$('.terms-index-section-hit[data-section]');
  const sectionBlocks = $$('.terms-index-section');
  const TERMS_INDEX_BASE = '/terms/';

  const SECTION_META = {
    term: { col1: '用語', col3: '定義', unit: '語' },
    comparison: { col1: '項目', col3: '概要', unit: '項目' },
    numeric: { col1: '項目', col3: '概要', unit: '項目' },
    mistake: { col1: '項目', col3: '概要', unit: '項目' },
  };

  let activeCat = 'all';
  let urlSyncTimer = null;
  const DEBOUNCE_MS = 150;
  let inputDebounceTimer = null;

  const norm = (s) => (s || '').toString().trim().toLowerCase();

  function parseSearchTokens(raw) {
    const parts = norm(raw).split(/\s+/).filter(Boolean);
    const inc = [];
    const exc = [];
    parts.forEach((p) => {
      if (p.startsWith('-') && p.length > 1) exc.push(p.slice(1));
      else inc.push(p);
    });
    return { inc, exc };
  }

  function matchesSearch(item, tokens) {
    const hay = norm(item.search);
    if (tokens.inc.length && !tokens.inc.every((t) => hay.includes(t))) return false;
    if (tokens.exc.some((t) => hay.includes(t))) return false;
    return true;
  }

  function itemVisible(item) {
    const tokens = parseSearchTokens(q?.value || '');
    const catOk = activeCat === 'all' || item.category === activeCat;
    return catOk && matchesSearch(item, tokens);
  }

  function hasActiveFilters() {
    return !!(q?.value || '').trim() || activeCat !== 'all';
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function highlightText(text, query) {
    const raw = (text || '').toString();
    const tokens = parseSearchTokens(query).inc.filter((t) => t.length >= 1);
    if (!tokens.length) return escapeHtml(raw);
    let spans = [{ start: 0, end: raw.length, hl: false }];
    tokens.forEach((tok) => {
      const next = [];
      spans.forEach((sp) => {
        if (sp.hl) {
          next.push(sp);
          return;
        }
        const slice = raw.slice(sp.start, sp.end);
        const sliceLower = slice.toLowerCase();
        let idx = 0;
        while (idx < slice.length) {
          const at = sliceLower.indexOf(tok, idx);
          if (at < 0) {
            next.push({ start: sp.start + idx, end: sp.end, hl: false });
            break;
          }
          if (at > idx) next.push({ start: sp.start + idx, end: sp.start + at, hl: false });
          next.push({ start: sp.start + at, end: sp.start + at + tok.length, hl: true });
          idx = at + tok.length;
        }
      });
      spans = next;
    });
    return spans
      .map((sp) => {
        const part = raw.slice(sp.start, sp.end);
        return sp.hl ? `<mark class="terms-hit-mark">${escapeHtml(part)}</mark>` : escapeHtml(part);
      })
      .join('');
  }

  function sortItems(list) {
    return [...list].sort((a, b) => {
      const c = a.category.localeCompare(b.category, 'ja');
      if (c) return c;
      return a.term.localeCompare(b.term, 'ja');
    });
  }

  function resolveEntryHref(href) {
    if (!href) return href;
    if (/^https?:\/\//i.test(href) || href.startsWith('/')) return href;
    return `${TERMS_INDEX_BASE}${String(href).replace(/^\.\//, '')}`;
  }

  function sectionItems(sectionId) {
    return sortItems(
      ITEMS.filter((item) => (item.sections || ['term']).includes(sectionId) && itemVisible(item))
    );
  }

  function sectionTotal(sectionId) {
    return ITEMS.filter((item) => (item.sections || ['term']).includes(sectionId)).length;
  }

  function rowHtml(item, query, sectionId, mode) {
    const meta = SECTION_META[sectionId] || SECTION_META.term;
    const href = resolveEntryHref(item.href);
    const hrefAttr = ` data-entry-href="${escapeHtml(href)}"`;
    const col3 =
      mode === 'summary'
        ? item.summary || item.shortDef || ''
        : item.shortDef || item.definition || '';
    const col3Class = mode === 'summary' ? 'terms-idx-td-summary' : 'terms-idx-td-snippet';
    return `<tr class="terms-idx-table-row">
<td class="terms-idx-td-term" data-label="${escapeHtml(meta.col1)}"${hrefAttr} tabindex="0"><div class="terms-idx-term-cell"><a href="${escapeHtml(href)}">${highlightText(item.term, query)}</a></div></td>
<td class="terms-idx-td-cat" data-label="分野"${hrefAttr}>${escapeHtml(item.category)}</td>
<td class="${col3Class}" data-label="${escapeHtml(meta.col3)}"${hrefAttr}>${col3 ? highlightText(col3, query) : ''}</td>
</tr>`;
  }

  function bindRows(root) {
    if (!root) return;
    const go = (href) => {
      const target = resolveEntryHref(href);
      if (target) window.location.href = target;
    };
    root.querySelectorAll('[data-entry-href]').forEach((cell) => {
      if (cell.dataset.bound) return;
      cell.dataset.bound = '1';
      const href = cell.dataset.entryHref;
      cell.addEventListener('click', (e) => {
        if (e.target.closest('a')) return;
        go(href);
      });
      if (cell.classList.contains('terms-idx-td-term')) {
        cell.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            go(href);
          }
        });
      }
      cell.addEventListener('mouseenter', () => {
        root.querySelectorAll(`[data-entry-href="${CSS.escape(href)}"]`).forEach((c) => {
          c.classList.add('is-entry-hover');
        });
      });
      cell.addEventListener('mouseleave', () => {
        root.querySelectorAll(`[data-entry-href="${CSS.escape(href)}"]`).forEach((c) => {
          c.classList.remove('is-entry-hover');
        });
      });
    });
  }

  function renderActiveFilters() {
    if (!activeFilters) return;
    const tags = [];
    const query = (q?.value || '').trim();
    if (query) tags.push({ type: 'q', label: `検索: ${query}` });
    if (activeCat !== 'all') tags.push({ type: 'cat', label: activeCat });
    if (!tags.length) {
      activeFilters.classList.add('hide');
      activeFilters.innerHTML = '';
      return;
    }
    activeFilters.classList.remove('hide');
    activeFilters.innerHTML =
      '<span class="terms-idx-active-label">適用中</span>' +
      tags
        .map(
          (t) =>
            `<button type="button" class="terms-idx-active-tag" data-remove="${t.type}">${escapeHtml(t.label)}<span aria-hidden="true">×</span></button>`
        )
        .join('');
    activeFilters.querySelectorAll('[data-remove]').forEach((btn) => {
      btn.addEventListener('click', () => {
        if (btn.dataset.remove === 'q' && q) q.value = '';
        if (btn.dataset.remove === 'cat') {
          activeCat = 'all';
          chips.forEach((b) => b.classList.toggle('on', (b.dataset.cat || 'all') === 'all'));
        }
        syncClear();
        apply();
      });
    });
  }

  function syncUrl() {
    if (urlSyncTimer) clearTimeout(urlSyncTimer);
    urlSyncTimer = setTimeout(() => {
      const params = new URLSearchParams();
      const query = (q?.value || '').trim();
      if (query) params.set('q', query);
      if (activeCat !== 'all') params.set('cat', activeCat);
      const qs = params.toString();
      const next = qs ? `${TERMS_INDEX_BASE}?${qs}` : TERMS_INDEX_BASE;
      history.replaceState(null, '', next);
    }, 200);
  }

  function readUrl() {
    const params = new URLSearchParams(location.search);
    if (params.has('q') && q) q.value = params.get('q') || '';
    activeCat = params.get('cat') || 'all';
    chips.forEach((b) => b.classList.toggle('on', (b.dataset.cat || 'all') === activeCat));
  }

  function renderTables(query) {
    let totalShown = 0;
    sectionBodies.forEach((body) => {
      const sectionId = body.dataset.section || 'term';
      const mode = body.dataset.mode || 'definition';
      const visible = sectionItems(sectionId);
      totalShown += visible.length;
      body.innerHTML = visible.map((item) => rowHtml(item, query, sectionId, mode)).join('');
      bindRows(body);

      const total = sectionTotal(sectionId);
      const meta = SECTION_META[sectionId] || SECTION_META.term;
      const hitEl = sectionHits.find((el) => el.dataset.section === sectionId);
      if (hitEl) hitEl.textContent = `${visible.length} / ${total} ${meta.unit}`;

      const block = sectionBlocks.find((el) => el.id === `terms-idx-section-${sectionId}`);
      if (block) block.classList.toggle('is-empty', visible.length === 0);
    });
    return totalShown;
  }

  function apply(syncUrlFlag = true) {
    const query = q?.value || '';
    const shown = renderTables(query);
    const total = ITEMS.length;

    if (hit) hit.textContent = `${shown} / ${total} 語`;
    if (empty) {
      const hideEmpty = shown !== 0;
      empty.classList.toggle('hide', hideEmpty);
      if (hideEmpty) empty.setAttribute('hidden', '');
      else empty.removeAttribute('hidden');
    }
    renderActiveFilters();
    syncReset();
    if (syncUrlFlag) syncUrl();
  }

  function syncClear() {
    if (!clearBtn || !q) return;
    clearBtn.classList.toggle('hide', !(q.value || '').trim());
  }

  function syncReset() {
    if (toolbarReset) toolbarReset.classList.toggle('hide', !hasActiveFilters());
  }

  function resetAll() {
    if (q) q.value = '';
    activeCat = 'all';
    chips.forEach((b) => b.classList.toggle('on', (b.dataset.cat || 'all') === 'all'));
    syncClear();
    apply();
    q?.focus();
  }

  if (ITEMS.length >= 60) {
    document.body.classList.add('terms-index-large');
  }

  q?.addEventListener('input', () => {
    syncClear();
    if (inputDebounceTimer) clearTimeout(inputDebounceTimer);
    inputDebounceTimer = setTimeout(() => {
      inputDebounceTimer = null;
      apply();
    }, DEBOUNCE_MS);
  });
  clearBtn?.addEventListener('click', () => {
    if (!q) return;
    q.value = '';
    syncClear();
    apply();
    q.focus();
  });
  toolbarReset?.addEventListener('click', resetAll);
  document.getElementById('terms-idx-empty-reset')?.addEventListener('click', resetAll);

  chips.forEach((btn) => {
    btn.addEventListener('click', () => {
      chips.forEach((b) => b.classList.remove('on'));
      btn.classList.add('on');
      activeCat = btn.dataset.cat || 'all';
      apply();
    });
  });

  document.addEventListener('keydown', (e) => {
    const tag = (e.target && e.target.tagName) || '';
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(tag) || e.target?.isContentEditable;
    if (e.key === '/' && !typing) {
      e.preventDefault();
      q?.focus();
      return;
    }
    if (e.key !== 'Escape' || typing) return;
    if (document.activeElement === q && q?.value) {
      q.value = '';
      syncClear();
      apply();
      return;
    }
    if (hasActiveFilters()) resetAll();
  });

  if (toolbar) {
    const onScroll = () => {
      toolbar.classList.toggle('is-scrolled', toolbar.getBoundingClientRect().top <= 56);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  topBtn?.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  window.addEventListener(
    'scroll',
    () => {
      if (!topBtn) return;
      topBtn.classList.toggle('is-visible', window.scrollY > 480);
    },
    { passive: true }
  );

  readUrl();
  syncClear();
  apply(false);
})();
