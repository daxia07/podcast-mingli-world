/* theme.js — the light/dark setting.
 *
 * Three states, not two. "System" is the default and the one most people want;
 * the explicit choices exist because a phone that auto-switches at sunset should
 * not be able to override a deliberate preference.
 *
 *   system  no data-theme attribute — CSS follows prefers-color-scheme
 *   light   data-theme="light"      — pinned light on a dark phone
 *   dark    data-theme="dark"       — pinned dark on a light phone
 *
 * The attribute goes on <html> before first paint (see the inline snippet in
 * index.html) so there is no white flash on a dark phone. This file re-applies
 * it, keeps the address-bar colour in step, and drives the Account control.
 *
 * Everything above `install()` is pure so the rules are testable without a DOM.
 */
(function () {
  'use strict';

  var KEY = 'pod_theme';
  var CHOICES = ['system', 'light', 'dark'];

  // Kept in step with --bg in style.css; the browser paints the status bar and
  // the address bar with this before any CSS is parsed.
  var BAR = { light: '#f7f6f3', dark: '#0f1116' };

  function normalise(pref) {
    return CHOICES.indexOf(pref) === -1 ? 'system' : pref;
  }

  /* What the user will actually see, given the setting and the OS. */
  function effective(pref, systemDark) {
    var p = normalise(pref);
    if (p === 'system') return systemDark ? 'dark' : 'light';
    return p;
  }

  /* The value for the data-theme attribute — null means "let CSS decide". */
  function attribute(pref) {
    var p = normalise(pref);
    return p === 'system' ? null : p;
  }

  function barColor(pref, systemDark) {
    return BAR[effective(pref, systemDark)];
  }

  // ——— stateful bits ———

  function read() {
    try {
      return normalise(localStorage.getItem(KEY));
    } catch (e) {
      return 'system';
    }
  }

  function systemPrefersDark() {
    return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  }

  function apply(pref) {
    var root = document.documentElement;
    var attr = attribute(pref);
    if (attr) root.setAttribute('data-theme', attr);
    else root.removeAttribute('data-theme');

    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', barColor(pref, systemPrefersDark()));
  }

  function set(pref) {
    var p = normalise(pref);
    try {
      localStorage.setItem(KEY, p);
    } catch (e) {}
    apply(p);
    window.dispatchEvent(new CustomEvent('theme:change', { detail: { pref: p } }));
    return p;
  }

  function install() {
    apply(read());

    // On "system", follow the phone as it flips at sunset without a reload.
    if (window.matchMedia) {
      var mq = window.matchMedia('(prefers-color-scheme: dark)');
      var onChange = function () {
        if (read() === 'system') apply('system');
      };
      if (mq.addEventListener) mq.addEventListener('change', onChange);
      else if (mq.addListener) mq.addListener(onChange);
    }

    var seg = document.getElementById('themeSeg');
    if (!seg) return;
    var sync = function () {
      var pref = read();
      seg.querySelectorAll('[data-theme-choice]').forEach(function (btn) {
        var on = btn.dataset.themeChoice === pref;
        btn.classList.toggle('on', on);
        btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
    };
    seg.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-theme-choice]');
      if (!btn) return;
      set(btn.dataset.themeChoice);
      sync();
    });
    sync();
  }

  window.Theme = {
    KEY: KEY,
    CHOICES: CHOICES,
    BAR: BAR,
    normalise: normalise,
    effective: effective,
    attribute: attribute,
    barColor: barColor,
    read: read,
    set: set,
    apply: apply,
    install: install
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install);
  } else {
    install();
  }
})();
