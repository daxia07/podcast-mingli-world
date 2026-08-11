/* player-ui.js — chapters, transcript, and native-feel behaviour.
 *
 * Self-contained: app.js only has to dispatch `episode:change` when playback
 * starts. Everything here degrades to nothing when an episode has no chapter
 * or transcript artifact, which is most of the back catalogue.
 *
 * Depends on window.VTT (vtt.js) and window.Chapters (chapters.js).
 */
(function () {
  'use strict';

  var audio = document.getElementById('audio');
  if (!audio) return;

  var state = {
    episode: null,
    chapters: [],
    cues: [],
    activeChapter: -1,
    activeCue: -1,
    autoScroll: true,
    autoScrollTimer: 0,
    sleepAt: 0,
    sleepEndOfEpisode: false
  };

  function $(id) { return document.getElementById(id); }
  function slugOf(ep) {
    if (!ep) return null;
    return ep.slug || String(ep.filename || '').replace(/\.mp3$/, '') || null;
  }

  // Vibration is a no-op on iOS; harmless, and a real cue on Android.
  function tap(ms) { if (navigator.vibrate) { try { navigator.vibrate(ms || 8); } catch (e) {} } }

  // ——— loading side artifacts ———

  function fetchJSON(url) {
    return fetch(url).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  }
  function fetchText(url) {
    return fetch(url).then(function (r) { return r.ok ? r.text() : null; }).catch(function () { return null; });
  }

  function loadEpisode(ep) {
    state.episode = ep;
    state.chapters = [];
    state.cues = [];
    state.activeChapter = -1;
    state.activeCue = -1;

    render();

    var slug = slugOf(ep);
    if (!slug) return;

    if (ep.has_chapters !== false) {
      fetchJSON('/chapters/' + slug + '.json').then(function (doc) {
        if (!doc || slugOf(state.episode) !== slug) return;
        state.chapters = window.Chapters.normalize(doc, audio.duration || 0);
        renderRail();
        renderChapterList();
        updateChrome();
      });
    }

    if (ep.has_transcript !== false) {
      fetchText('/transcripts/' + slug + '.vtt').then(function (text) {
        if (!text || slugOf(state.episode) !== slug) return;
        state.cues = window.VTT.parse(text);
        renderTranscript();
        updateTabAvailability();
      });
    }
  }

  // ——— chapter rail on the seek bar ———

  function renderRail() {
    var rail = $('chapterRail');
    if (!rail) return;
    var duration = audio.duration || 0;
    var segs = window.Chapters.segments(state.chapters, duration);

    if (!segs.length) { rail.innerHTML = ''; rail.hidden = true; return; }

    rail.hidden = false;
    rail.innerHTML = segs.map(function (s) {
      return '<button type="button" class="rail-seg" data-idx="' + s.index +
        '" style="left:' + s.left.toFixed(3) + '%;width:' + s.width.toFixed(3) + '%"' +
        ' title="' + escapeAttr(s.title) + '" aria-label="' + escapeAttr(s.title) + '">' +
        '<span class="rail-fill"></span></button>';
    }).join('');
  }

  function updateRail(t) {
    var rail = $('chapterRail');
    if (!rail || rail.hidden) return;
    var idx = window.Chapters.indexAt(state.chapters, t);
    var within = window.Chapters.progressWithin(state.chapters, t);
    var segs = rail.children;

    for (var i = 0; i < segs.length; i++) {
      var done = i < idx;
      var active = i === idx;
      segs[i].classList.toggle('done', done);
      segs[i].classList.toggle('active', active);
      var fill = segs[i].firstChild;
      if (fill) fill.style.width = done ? '100%' : active ? (within * 100).toFixed(2) + '%' : '0%';
    }
  }

  // ——— chapter list sheet ———

  function renderChapterList() {
    var list = $('chapterList');
    if (!list) return;
    if (!state.chapters.length) {
      list.innerHTML = '<p class="sheet-empty">No chapters for this episode.</p>';
      return;
    }
    list.innerHTML = state.chapters.map(function (c, i) {
      return '<button type="button" class="chapter-row" data-idx="' + i + '">' +
        '<span class="chapter-no">' + (i + 1) + '</span>' +
        '<span class="chapter-title">' + escapeHtml(c.title) + '</span>' +
        '<span class="chapter-time">' + window.Chapters.formatTime(c.start) + '</span>' +
        '</button>';
    }).join('');
  }

  function updateChapterList(idx) {
    var list = $('chapterList');
    if (!list) return;
    for (var i = 0; i < list.children.length; i++) {
      list.children[i].classList.toggle('on', i === idx);
    }
  }

  // ——— transcript ———

  function renderTranscript() {
    var el = $('transcriptBody');
    if (!el) return;
    if (!state.cues.length) {
      el.innerHTML = '<p class="sheet-empty">No transcript for this episode yet.</p>';
      return;
    }
    el.innerHTML = state.cues.map(function (c, i) {
      var who = c.speaker
        ? '<span class="cue-who cue-who-' + escapeAttr(c.speaker.toLowerCase()) + '">' + escapeHtml(c.speaker) + '</span>'
        : '';
      return '<p class="cue" data-idx="' + i + '" data-start="' + c.start + '">' + who +
        '<span class="cue-text">' + escapeHtml(c.text) + '</span></p>';
    }).join('');
  }

  function updateTranscript(t) {
    if (!state.cues.length) return;
    var idx = window.VTT.activeIndex(state.cues, t);
    if (idx === state.activeCue) return;

    var el = $('transcriptBody');
    if (!el) return;
    var prev = el.querySelector('.cue.on');
    if (prev) prev.classList.remove('on');
    state.activeCue = idx;
    if (idx < 0) return;

    var node = el.children[idx];
    if (!node) return;
    node.classList.add('on');

    if (state.autoScroll && !$('panelSheet').hidden) {
      node.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }
  }

  // ——— chrome ———

  function updateChrome() {
    var label = $('chapterNow');
    if (!label) return;
    var idx = window.Chapters.indexAt(state.chapters, audio.currentTime || 0);
    if (idx === -1) { label.hidden = true; return; }
    label.hidden = false;
    label.textContent = state.chapters[idx].title;
  }

  function updateTabAvailability() {
    setTabEnabled('chapters', state.chapters.length > 0);
    setTabEnabled('transcript', state.cues.length > 0);
  }

  function setTabEnabled(name, enabled) {
    // Two buttons per panel: the chip in the toolbar and the tab in the sheet.
    var btns = document.querySelectorAll('.panel-tab[data-panel="' + name + '"]');
    for (var i = 0; i < btns.length; i++) {
      btns[i].disabled = !enabled;
      btns[i].classList.toggle('disabled', !enabled);
    }
  }

  function render() {
    renderRail();
    renderChapterList();
    renderTranscript();
    updateChrome();
    updateTabAvailability();
  }

  // ——— Media Session: lock screen + headphone controls ———

  function updateMediaSession(ep) {
    if (!('mediaSession' in navigator) || !ep) return;
    try {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: ep.title || 'Episode',
        artist: (ep.playlist || 'Mingli').replace(/-/g, ' '),
        album: 'podcast.mingli.world',
        artwork: [{ src: '/artwork.jpg', sizes: '1400x1400', type: 'image/jpeg' }]
      });
      navigator.mediaSession.setActionHandler('play', function () { audio.play(); });
      navigator.mediaSession.setActionHandler('pause', function () { audio.pause(); });
      navigator.mediaSession.setActionHandler('seekbackward', function () {
        audio.currentTime = Math.max(0, audio.currentTime - 15);
      });
      navigator.mediaSession.setActionHandler('seekforward', function () {
        audio.currentTime = Math.min(audio.duration || 0, audio.currentTime + 15);
      });
      navigator.mediaSession.setActionHandler('seekto', function (d) {
        if (d.seekTime != null) audio.currentTime = d.seekTime;
      });
      // Chapter skip beats track skip on a 60-minute episode.
      navigator.mediaSession.setActionHandler('nexttrack', jumpNextChapter);
      navigator.mediaSession.setActionHandler('previoustrack', jumpPrevChapter);
    } catch (e) { /* older browsers ignore unsupported actions */ }
  }

  function updatePositionState() {
    if (!('mediaSession' in navigator) || !navigator.mediaSession.setPositionState) return;
    if (!audio.duration || !isFinite(audio.duration)) return;
    try {
      navigator.mediaSession.setPositionState({
        duration: audio.duration,
        playbackRate: audio.playbackRate || 1,
        position: Math.min(audio.currentTime, audio.duration)
      });
    } catch (e) {}
  }

  // ——— chapter navigation ———

  function jumpNextChapter() {
    var next = window.Chapters.nextStart(state.chapters, audio.currentTime);
    audio.currentTime = next == null ? (audio.duration || audio.currentTime) : next;
    tap();
  }

  function jumpPrevChapter() {
    audio.currentTime = window.Chapters.previousStart(state.chapters, audio.currentTime);
    tap();
  }

  // ——— sleep timer ———

  function setSleep(minutes, endOfEpisode) {
    state.sleepEndOfEpisode = !!endOfEpisode;
    state.sleepAt = minutes ? Date.now() + minutes * 60000 : 0;
    var chip = $('btnSleep');
    if (chip) {
      chip.classList.toggle('on', !!(state.sleepAt || endOfEpisode));
      chip.textContent = endOfEpisode ? 'End' : state.sleepAt ? minutes + 'm' : 'Sleep';
    }
  }

  function checkSleep() {
    if (state.sleepAt && Date.now() >= state.sleepAt) {
      audio.pause();
      setSleep(0, false);
    }
  }

  // ——— drag-to-dismiss on the full player ———

  function wireDrag() {
    var sheet = $('playerFull');
    var handle = $('playerGrip') || $('playerFull');
    if (!sheet || !handle) return;

    var startY = 0, dy = 0, dragging = false, startedAt = 0;

    handle.addEventListener('pointerdown', function (e) {
      // Only from the grip area, and never while the panel is scrolled.
      if (e.target.closest('.panel-sheet, .rail-seg, button, input')) return;
      dragging = true; startY = e.clientY; dy = 0; startedAt = Date.now();
      sheet.classList.add('dragging');
    });

    window.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      dy = Math.max(0, e.clientY - startY);
      // Rubber-band: resistance grows the further you pull.
      var eased = dy < 0 ? 0 : dy;
      sheet.style.transform = 'translateY(' + eased + 'px)';
    });

    function release() {
      if (!dragging) return;
      dragging = false;
      sheet.classList.remove('dragging');
      sheet.style.transform = '';

      var velocity = dy / Math.max(1, Date.now() - startedAt);
      if (dy > 140 || velocity > 0.6) {
        sheet.hidden = true;
        tap(12);
      }
      dy = 0;
    }

    window.addEventListener('pointerup', release);
    window.addEventListener('pointercancel', release);
  }

  // ——— theme ———

  function applyTheme(mode) {
    var root = document.documentElement;
    if (mode === 'dark' || mode === 'light') root.setAttribute('data-theme', mode);
    else root.removeAttribute('data-theme');
    try { localStorage.setItem('pod_theme', mode); } catch (e) {}
    var btn = $('btnTheme');
    if (btn) btn.textContent = mode === 'dark' ? 'Dark' : mode === 'light' ? 'Light' : 'System';
  }

  function initTheme() {
    var saved = 'system';
    try { saved = localStorage.getItem('pod_theme') || 'system'; } catch (e) {}
    applyTheme(saved);
  }

  // ——— events ———

  audio.addEventListener('timeupdate', function () {
    var t = audio.currentTime || 0;
    updateRail(t);
    updateTranscript(t);

    var idx = window.Chapters.indexAt(state.chapters, t);
    if (idx !== state.activeChapter) {
      state.activeChapter = idx;
      updateChrome();
      updateChapterList(idx);
    }
    checkSleep();
  });

  audio.addEventListener('loadedmetadata', function () {
    // Chapter geometry is a function of duration, unknown until now.
    if (state.chapters.length) {
      state.chapters = window.Chapters.normalize(
        { chapters: state.chapters.map(function (c) { return { startTime: c.start, endTime: c.end, title: c.title }; }) },
        audio.duration || 0
      );
      renderRail();
    }
    updatePositionState();
  });

  audio.addEventListener('play', updatePositionState);
  audio.addEventListener('ratechange', updatePositionState);
  audio.addEventListener('ended', function () {
    if (state.sleepEndOfEpisode) { audio.pause(); setSleep(0, false); }
  });

  window.addEventListener('episode:change', function (e) {
    loadEpisode(e.detail);
    updateMediaSession(e.detail);
  });

  document.addEventListener('click', function (e) {
    var seg = e.target.closest('.rail-seg');
    if (seg) {
      audio.currentTime = state.chapters[+seg.dataset.idx].start;
      tap();
      return;
    }

    var row = e.target.closest('.chapter-row');
    if (row) {
      audio.currentTime = state.chapters[+row.dataset.idx].start;
      tap();
      return;
    }

    var cue = e.target.closest('.cue');
    if (cue) {
      audio.currentTime = parseFloat(cue.dataset.start) || 0;
      state.autoScroll = true;
      tap();
      return;
    }

    var tab = e.target.closest('.panel-tab');
    if (tab && !tab.disabled) {
      showPanel(tab.dataset.panel);
      return;
    }

    if (e.target.closest('#btnChapterNext')) return jumpNextChapter();
    if (e.target.closest('#btnChapterPrev')) return jumpPrevChapter();
    if (e.target.closest('#panelClose')) { $('panelSheet').hidden = true; return; }

    var sleepOpt = e.target.closest('[data-sleep]');
    if (sleepOpt) {
      var v = sleepOpt.dataset.sleep;
      setSleep(v === 'end' ? 0 : parseInt(v, 10), v === 'end');
      $('sleepSheet').hidden = true;
      return;
    }
    if (e.target.closest('#btnSleep')) { $('sleepSheet').hidden = !$('sleepSheet').hidden; return; }

    if (e.target.closest('#btnTheme')) {
      var order = ['system', 'light', 'dark'];
      var cur = 'system';
      try { cur = localStorage.getItem('pod_theme') || 'system'; } catch (err) {}
      applyTheme(order[(order.indexOf(cur) + 1) % order.length]);
      return;
    }
  });

  // Manual scrolling suspends follow-along, so reading ahead isn't yanked back.
  var body = $('transcriptBody');
  if (body) {
    body.addEventListener('scroll', function () {
      state.autoScroll = false;
      clearTimeout(state.autoScrollTimer);
      state.autoScrollTimer = setTimeout(function () { state.autoScroll = true; }, 4000);
    }, { passive: true });
  }

  var search = $('transcriptSearch');
  if (search) {
    search.addEventListener('input', function () {
      var hits = window.VTT.search(state.cues, this.value);
      var el = $('transcriptBody');
      if (!el) return;
      for (var i = 0; i < el.children.length; i++) el.children[i].classList.remove('hit');
      for (var j = 0; j < hits.length; j++) el.children[hits[j]].classList.add('hit');
      if (hits.length) el.children[hits[0]].scrollIntoView({ block: 'center', behavior: 'smooth' });
    });
  }

  function showPanel(name) {
    var sheet = $('panelSheet');
    if (!sheet) return;
    sheet.hidden = false;
    var tabs = document.querySelectorAll('.panel-tab');
    for (var i = 0; i < tabs.length; i++) tabs[i].classList.toggle('on', tabs[i].dataset.panel === name);
    var panes = document.querySelectorAll('.panel-pane');
    for (var j = 0; j < panes.length; j++) panes[j].hidden = panes[j].dataset.panel !== name;
    if (name === 'transcript' && state.activeCue >= 0) {
      var node = $('transcriptBody').children[state.activeCue];
      if (node) node.scrollIntoView({ block: 'center' });
    }
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function escapeAttr(s) { return escapeHtml(s).replace(/\n/g, ' '); }

  initTheme();
  wireDrag();

  window.PlayerUI = { showPanel: showPanel, state: state, setSleep: setSleep };
})();
