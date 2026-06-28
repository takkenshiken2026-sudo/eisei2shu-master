/**
 * 試験日検索ページ（exam-dates/index.html）— 会場・地域・年月で絞り込み
 */
(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const tbody = $('#exam-schedule-list tbody');
  if (!tbody) return;

  const sortEl = $('#exam-schedule-sort');
  const venueInput = $('#exam-schedule-venue-input');
  const venueBox = $('#exam-schedule-venue-box');
  const venueList = $('#exam-schedule-venue-list');
  const venueClear = $('#exam-schedule-venue-clear');
  const venueToggle = $('#exam-schedule-venue-toggle');
  const monthEl = $('#exam-schedule-month');
  const countEl = $('#exam-schedule-count');
  const emptyEl = $('#exam-schedule-empty');

  let venueId = '';
  let region = '';
  let allRows = $$('#exam-schedule-list tbody tr');

  function normalize(s) {
    return String(s || '').trim().toLowerCase();
  }

  function formatCount(n, total) {
    if (n === total) return `全${total}件`;
    return `${n}件 / 全${total}件`;
  }

  function rowMatches(row) {
    if (venueId && row.dataset.venueId !== venueId) return false;
    if (region && row.dataset.region !== region) return false;
    if (monthEl && monthEl.value) {
      const prefix = monthEl.value;
      if (!String(row.dataset.date || '').startsWith(prefix)) return false;
    }
    if (venueInput && venueInput.value.trim() && !venueId) {
      const q = normalize(venueInput.value);
      const name = normalize(row.dataset.venueName);
      if (!name.includes(q)) return false;
    }
    return true;
  }

  function sortRows(rows) {
    const mode = sortEl ? sortEl.value : 'date-asc';
    const copy = rows.slice();
    copy.sort((a, b) => {
      if (mode === 'venue') {
        const va = a.dataset.venueName || '';
        const vb = b.dataset.venueName || '';
        const cmp = va.localeCompare(vb, 'ja');
        if (cmp !== 0) return cmp;
      }
      const da = a.dataset.date || '';
      const db = b.dataset.date || '';
      if (mode === 'date-desc') return db.localeCompare(da);
      return da.localeCompare(db);
    });
    return copy;
  }

  function filterCalendarBlocks() {
    $$('.exam-schedule-venue-block').forEach((block) => {
      const matchVenue = !venueId || block.dataset.venueId === venueId;
      const matchRegion = !region || block.dataset.region === region;
      block.hidden = !(matchVenue && matchRegion);
    });
  }

  function render() {
    const visible = allRows.filter(rowMatches);
    const sorted = sortRows(visible);
    tbody.innerHTML = '';
    sorted.forEach((row) => tbody.appendChild(row));
    allRows.forEach((row) => {
      row.hidden = !visible.includes(row);
    });
    if (countEl) countEl.textContent = formatCount(visible.length, allRows.length);
    if (emptyEl) emptyEl.classList.toggle('hide', visible.length > 0);
    filterCalendarBlocks();
  }

  function setVenueOption(option) {
    if (!option) return;
    venueId = option.dataset.value || '';
    if (venueInput) venueInput.value = venueId ? option.dataset.label || option.textContent.trim() : '';
    $$('#exam-schedule-venue-list .exam-schedule-pref-option').forEach((el) => {
      el.classList.toggle('on', el === option);
    });
    if (venueClear) venueClear.classList.toggle('hide', !venueId && !venueInput.value.trim());
    closeVenueList();
    render();
  }

  function openVenueList() {
    if (!venueBox || !venueList) return;
    venueBox.classList.add('open');
    venueList.classList.remove('hide');
    if (venueInput) venueInput.setAttribute('aria-expanded', 'true');
  }

  function closeVenueList() {
    if (!venueBox || !venueList) return;
    venueBox.classList.remove('open');
    venueList.classList.add('hide');
    if (venueInput) venueInput.setAttribute('aria-expanded', 'false');
  }

  function filterVenueOptions() {
    const q = normalize(venueInput ? venueInput.value : '');
    $$('#exam-schedule-venue-list .exam-schedule-pref-option').forEach((opt) => {
      if (!opt.dataset.value) {
        opt.hidden = false;
        return;
      }
      const label = normalize(opt.dataset.label || opt.textContent);
      opt.hidden = q ? !label.includes(q) : false;
    });
  }

  if (sortEl) sortEl.addEventListener('change', render);
  if (monthEl) monthEl.addEventListener('change', render);

  if (venueInput) {
    venueInput.addEventListener('focus', () => {
      filterVenueOptions();
      openVenueList();
    });
    venueInput.addEventListener('input', () => {
      venueId = '';
      filterVenueOptions();
      openVenueList();
      if (venueClear) venueClear.classList.remove('hide');
      render();
    });
  }

  if (venueToggle) {
    venueToggle.addEventListener('click', () => {
      if (venueBox && venueBox.classList.contains('open')) closeVenueList();
      else openVenueList();
    });
  }

  if (venueClear) {
    venueClear.addEventListener('click', () => {
      venueId = '';
      if (venueInput) venueInput.value = '';
      venueClear.classList.add('hide');
      setVenueOption($('#exam-schedule-venue-list .exam-schedule-pref-option[data-value=""]'));
    });
  }

  if (venueList) {
    venueList.addEventListener('click', (e) => {
      const opt = e.target.closest('.exam-schedule-pref-option');
      if (opt) setVenueOption(opt);
    });
  }

  document.addEventListener('click', (e) => {
    if (!venueBox || venueBox.contains(e.target)) return;
    closeVenueList();
  });

  $$('.exam-schedule-region-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      region = chip.dataset.region || '';
      $$('.exam-schedule-region-chip').forEach((c) => c.classList.toggle('on', c === chip));
      render();
    });
  });

  render();
})();
