// Google Analytics 4
// - 測定ID: site-config.json → SITE_CONFIG.ga4MeasurementId / window.__GA4_MEASUREMENT_ID__
// - index.html は <head> の Google タグと併用（SPA 用 ga4PageView）
(function () {
  var DEFAULT_MID = "G-NYDT6H7XR8";
  var raw = "";
  try {
    if (typeof window !== "undefined" && window.__GA4_MEASUREMENT_ID__ != null) {
      raw = String(window.__GA4_MEASUREMENT_ID__).trim();
    }
    if (!raw && typeof window !== "undefined" && window.SITE_CONFIG && window.SITE_CONFIG.ga4MeasurementId != null) {
      raw = String(window.SITE_CONFIG.ga4MeasurementId).trim();
    }
  } catch (_e) {}
  if (!raw) raw = DEFAULT_MID;
  var MID = /^G-[A-Za-z0-9]+$/.test(raw) ? raw : "";
  if (!MID) return;

  function pageViewPayload(pagePath, pageTitle) {
    var path = pagePath != null && String(pagePath) ? String(pagePath) : "";
    if (!path && typeof location !== "undefined") {
      path = location.pathname + location.search + location.hash;
    }
    var title = pageTitle != null ? String(pageTitle) : typeof document !== "undefined" ? document.title : "";
    var o = { page_path: path, page_title: title };
    if (typeof location !== "undefined" && location.href) {
      o.page_location = location.href;
    }
    return o;
  }

  /**
   * SPA 等で URL・title が変わったあとに呼ぶ。index.html の gotoPage / popstate から利用。
   */
  function ga4PageView(pagePath, pageTitle) {
    if (typeof window.gtag !== "function") return;
    var o = pageViewPayload(pagePath, pageTitle);
    try {
      // GA4 SPA: 明示的 page_view（config だけよりレポートに載りやすい）
      window.gtag("event", "page_view", o);
    } catch (_e) {}
  }
  window.ga4PageView = ga4PageView;

  // <head> に Google タグを置いたページ（html_footer.ga4_head_snippet）では初期化済み
  if (window.__GA4_HEAD_INIT__ === MID) {
    return;
  }

  if (window.__GA4_SNIPPET_INIT__ === MID) return;
  window.__GA4_SNIPPET_INIT__ = MID;

  try {
    if (document.querySelector('script[src*="googletagmanager.com/gtag/js"][data-ga4-mid="' + MID + '"]')) {
      ga4PageView();
      return;
    }
  } catch (_e2) {}

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;
  gtag("js", new Date());

  var s = document.createElement("script");
  s.async = true;
  s.setAttribute("data-ga4-mid", MID);
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(MID);
  document.head.appendChild(s);

  try {
    gtag("config", MID, pageViewPayload());
  } catch (_e3) {}
})();
