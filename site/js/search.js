/* search.js — searching what was said, not just what an episode is called.
 *
 * Two corpora, one query:
 *
 *   metadata  every episode — title, subtitle, description, show, solution board
 *   moments   the 17 (and counting) episodes with an exact transcript: every
 *             spoken line and every chapter, each with the second it starts at
 *
 * The moment index (`/search-index.json`, built by scripts/build_search_index.py)
 * is ~100 KB, so app.js loads it lazily on the first keystroke in Search rather
 * than on boot. Everything here is pure: give it a query and the corpora and it
 * returns ranked results. The DOM lives in app.js.
 *
 * Matching is AND across terms — "vector database" must find both words — but a
 * term may be satisfied by the metadata *or* by a moment, so searching for a
 * concept that is only ever spoken aloud still finds the episode.
 */
(function () {
  'use strict';

  // A moment is only worth showing if the query is reasonably specific; single
  // letters match everything and turn the result list into the whole library.
  var MIN_TERM = 2;
  var SNIPPET_RADIUS = 90;
  var MAX_MOMENTS = 3;

  function normalise(s) {
    return String(s == null ? '' : s)
      .toLowerCase()
      .replace(/[‘’“”]/g, "'")
      .replace(/\s+/g, ' ')
      .trim();
  }

  /* Split a query into terms, honouring "quoted phrases" as single terms. */
  function terms(query) {
    var q = normalise(query);
    if (!q) return [];
    var out = [];
    var re = /"([^"]+)"|(\S+)/g;
    var m;
    while ((m = re.exec(q))) {
      var t = (m[1] || m[2]).replace(/^[^\w'-]+|[^\w'-]+$/g, '');
      if (t.length >= MIN_TERM) out.push(t);
    }
    return out;
  }

  /* The searchable text of an episode that is not its audio. */
  function metaBlob(ep, showTitle, board) {
    var parts = [ep.title, ep.subtitle, ep.description, ep.playlist, showTitle];
    if (board) {
      parts.push(board.title, board.problem);
      (board.sections || []).forEach(function (s) {
        parts.push(s.title);
        parts.push((s.body || []).join(' '));
      });
    }
    if (ep.keywords) parts.push([].concat(ep.keywords).join(' '));
    return normalise(parts.join(' '));
  }

  /* Which of `terms` appear in `haystack` (already normalised). */
  function hits(haystack, list) {
    var found = [];
    for (var i = 0; i < list.length; i++) {
      if (haystack.indexOf(list[i]) !== -1) found.push(list[i]);
    }
    return found;
  }

  /* Split text into {t, hit} chunks so the caller can escape then highlight. */
  function highlight(text, list) {
    if (!list.length) return [{ t: text, hit: false }];
    var lower = normalise(text);
    var marks = [];
    list.forEach(function (term) {
      var from = 0;
      var at;
      while ((at = lower.indexOf(term, from)) !== -1) {
        marks.push([at, at + term.length]);
        from = at + term.length;
      }
    });
    if (!marks.length) return [{ t: text, hit: false }];

    marks.sort(function (a, b) { return a[0] - b[0]; });
    var merged = [marks[0].slice()];
    for (var i = 1; i < marks.length; i++) {
      var last = merged[merged.length - 1];
      if (marks[i][0] <= last[1]) last[1] = Math.max(last[1], marks[i][1]);
      else merged.push(marks[i].slice());
    }

    var chunks = [];
    var cursor = 0;
    merged.forEach(function (range) {
      if (range[0] > cursor) chunks.push({ t: text.slice(cursor, range[0]), hit: false });
      chunks.push({ t: text.slice(range[0], range[1]), hit: true });
      cursor = range[1];
    });
    if (cursor < text.length) chunks.push({ t: text.slice(cursor), hit: false });
    return chunks;
  }

  /* A window of `text` around the first match, so long lines stay readable. */
  function snippet(text, list) {
    var lower = normalise(text);
    var first = -1;
    for (var i = 0; i < list.length; i++) {
      var at = lower.indexOf(list[i]);
      if (at !== -1 && (first === -1 || at < first)) first = at;
    }
    if (first === -1 || text.length <= SNIPPET_RADIUS * 2) return text;

    var start = Math.max(0, first - SNIPPET_RADIUS);
    var end = Math.min(text.length, first + SNIPPET_RADIUS);
    // Snap outwards to word boundaries rather than slicing mid-word.
    if (start > 0) {
      var space = text.indexOf(' ', start);
      if (space !== -1 && space < first) start = space + 1;
    }
    if (end < text.length) {
      var back = text.lastIndexOf(' ', end);
      if (back > first) end = back;
    }
    return (start > 0 ? '…' : '') + text.slice(start, end).trim() + (end < text.length ? '…' : '');
  }

  /* Ranked moments inside one episode's index entry. */
  function momentsFor(entry, list, limit) {
    if (!entry) return [];
    var found = [];

    function consider(pair, kind) {
      var text = pair[1];
      var matched = hits(normalise(text), list);
      if (!matched.length) return;
      found.push({
        t: pair[0],
        kind: kind,
        text: text,
        matched: matched.length,
        // A chapter title is a landmark: prefer it when it ties with a line.
        score: matched.length * 10 + (kind === 'chapter' ? 3 : 0)
      });
    }

    (entry.c || []).forEach(function (p) { consider(p, 'chapter'); });
    (entry.l || []).forEach(function (p) { consider(p, 'line'); });

    found.sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score;
      return a.t - b.t;
    });
    return found.slice(0, limit == null ? MAX_MOMENTS : limit);
  }

  /* Run a query across both corpora.
   *
   * ctx: { episodes, solutions, showTitle(id), index }
   * returns [{ ep, score, moments, momentCount }] ordered best first.
   */
  function run(query, ctx) {
    var list = terms(query);
    if (!list.length) return [];

    var index = (ctx.index && ctx.index.episodes) || {};
    var solutions = ctx.solutions || {};
    var showTitle = ctx.showTitle || function () { return ''; };
    var results = [];

    (ctx.episodes || []).forEach(function (ep) {
      var blob = metaBlob(ep, showTitle(ep.playlist), solutions[String(ep.id)]);
      var metaHits = hits(blob, list);
      var entry = index[String(ep.id)];
      var moments = entry ? momentsFor(entry, list, 40) : [];

      // AND across terms: every term must land somewhere in this episode.
      var covered = {};
      metaHits.forEach(function (t) { covered[t] = 1; });
      moments.forEach(function (m) {
        list.forEach(function (t) {
          if (normalise(m.text).indexOf(t) !== -1) covered[t] = 1;
        });
      });
      if (Object.keys(covered).length < list.length) return;

      var titleBlob = normalise(ep.title + ' ' + (ep.subtitle || ''));
      var score =
        hits(titleBlob, list).length * 100 +
        metaHits.length * 20 +
        Math.min(moments.length, 8) * 6;

      results.push({
        ep: ep,
        score: score,
        momentCount: moments.length,
        moments: moments.slice(0, MAX_MOMENTS)
      });
    });

    results.sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score;
      // Newest first among equals — recent work is usually what you meant.
      return String(b.ep.date || '').localeCompare(String(a.ep.date || ''));
    });
    return results;
  }

  window.Search = {
    MIN_TERM: MIN_TERM,
    MAX_MOMENTS: MAX_MOMENTS,
    normalise: normalise,
    terms: terms,
    metaBlob: metaBlob,
    hits: hits,
    highlight: highlight,
    snippet: snippet,
    momentsFor: momentsFor,
    run: run
  };
})();
