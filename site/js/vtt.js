/* vtt.js — WebVTT parsing and cue tracking for the transcript panel.
 *
 * Plain script, no build step, matching the rest of site/. Attaches to
 * window.VTT. Pure functions so the logic is unit-tested in tests/test_vtt.mjs
 * without a DOM.
 *
 * Transcripts come from scripts/lib/transcript.py, where cue text is what was
 * sent to TTS — so it is exact, not a recogniser's guess.
 */
(function (global) {
  'use strict';

  /** "00:01:02.500" | "01:02.500" -> seconds */
  function parseTimestamp(value) {
    var parts = String(value).trim().replace(',', '.').split(':');
    var h = 0, m = 0, s = 0;
    if (parts.length === 3) {
      h = parseInt(parts[0], 10); m = parseInt(parts[1], 10); s = parseFloat(parts[2]);
    } else if (parts.length === 2) {
      m = parseInt(parts[0], 10); s = parseFloat(parts[1]);
    } else {
      return 0;
    }
    if (isNaN(h) || isNaN(m) || isNaN(s)) return 0;
    return h * 3600 + m * 60 + s;
  }

  /** Parse a VTT document into [{start, end, speaker, text}]. */
  function parse(text) {
    if (!text) return [];
    var blocks = String(text).replace(/\r\n/g, '\n').split(/\n\s*\n/);
    var cues = [];

    for (var i = 0; i < blocks.length; i++) {
      var lines = blocks[i].split('\n').filter(function (l) { return l.trim(); });
      if (!lines.length) continue;
      if (/^WEBVTT/.test(lines[0])) continue;
      if (/^(NOTE|STYLE|REGION)\b/.test(lines[0])) continue;

      var timingIdx = -1;
      for (var j = 0; j < lines.length; j++) {
        if (lines[j].indexOf('-->') !== -1) { timingIdx = j; break; }
      }
      if (timingIdx === -1) continue;

      var bounds = lines[timingIdx].split('-->');
      var body = lines.slice(timingIdx + 1).join(' ').trim();
      if (!body) continue;

      var speaker = null;
      var voice = /^<v\s+([^>]*)>/.exec(body);
      if (voice) {
        speaker = voice[1].trim();
        body = body.slice(voice[0].length).trim();
      }
      // Strip any remaining cue tags — we render plain text.
      body = body.replace(/<\/?[^>]+>/g, '').trim();

      cues.push({
        start: parseTimestamp(bounds[0]),
        end: parseTimestamp((bounds[1] || '').trim().split(/\s+/)[0]),
        speaker: speaker,
        text: body
      });
    }
    return cues;
  }

  /** Index of the cue covering `t`, or -1.
   *
   * Binary search: called on every timeupdate (4x/sec) against transcripts
   * that run to ~900 cues on the hour-long episodes.
   */
  function activeIndex(cues, t) {
    if (!cues || !cues.length) return -1;
    var lo = 0, hi = cues.length - 1, best = -1;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      if (cues[mid].start <= t) { best = mid; lo = mid + 1; }
      else { hi = mid - 1; }
    }
    if (best === -1) return -1;
    // Past the end of the last cue and into a gap: nothing is active.
    if (t > cues[best].end && best === cues.length - 1) return -1;
    return best;
  }

  /** Cue indices whose text matches `query`, case-insensitive. */
  function search(cues, query) {
    var q = String(query || '').trim().toLowerCase();
    if (!q) return [];
    var hits = [];
    for (var i = 0; i < cues.length; i++) {
      if (cues[i].text.toLowerCase().indexOf(q) !== -1) hits.push(i);
    }
    return hits;
  }

  global.VTT = { parse: parse, parseTimestamp: parseTimestamp, activeIndex: activeIndex, search: search };
})(typeof window !== 'undefined' ? window : globalThis);
