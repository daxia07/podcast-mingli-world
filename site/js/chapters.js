/* chapters.js — chapter track logic for the seek bar and chapter sheet.
 *
 * Consumes the Podcasting 2.0 chapter documents written by
 * scripts/lib/chapters.py. Attaches to window.Chapters. Pure functions, tested
 * in tests/test_chapters_ui.mjs.
 */
(function (global) {
  'use strict';

  /** Normalise a chapters document into [{start, end, title}] sorted by start.
   *
   * `endTime` is optional in the spec, so a chapter without one runs to the
   * next chapter's start (or the episode duration for the last).
   */
  function normalize(doc, duration) {
    var raw = (doc && doc.chapters) || [];
    var list = raw
      .map(function (c) {
        return {
          start: Number(c.startTime) || 0,
          end: c.endTime != null ? Number(c.endTime) : null,
          title: String(c.title || '').trim() || 'Chapter'
        };
      })
      .sort(function (a, b) { return a.start - b.start; });

    for (var i = 0; i < list.length; i++) {
      if (list[i].end == null || list[i].end <= list[i].start) {
        list[i].end = i + 1 < list.length ? list[i + 1].start : (duration || list[i].start);
      }
    }
    return list;
  }

  /** Index of the chapter containing `t`, or -1. */
  function indexAt(chapters, t) {
    if (!chapters || !chapters.length) return -1;
    for (var i = 0; i < chapters.length; i++) {
      if (t >= chapters[i].start && t < chapters[i].end) return i;
    }
    // Exactly at (or past) the end belongs to the last chapter.
    return t >= chapters[chapters.length - 1].end ? chapters.length - 1 : -1;
  }

  /** Start time of the next chapter after `t`, or null at the end. */
  function nextStart(chapters, t) {
    for (var i = 0; i < chapters.length; i++) {
      if (chapters[i].start > t + 0.25) return chapters[i].start;
    }
    return null;
  }

  /** Start of the current chapter, or the previous one when already near its
   *  start — the behaviour every player uses for a "previous" control. */
  function previousStart(chapters, t, threshold) {
    var grace = threshold == null ? 3 : threshold;
    var idx = indexAt(chapters, t);
    if (idx <= 0) return 0;
    if (t - chapters[idx].start > grace) return chapters[idx].start;
    return chapters[idx - 1].start;
  }

  /** Seek-bar segment geometry as percentages of total duration. */
  function segments(chapters, duration) {
    if (!duration || !chapters || !chapters.length) return [];
    return chapters.map(function (c, i) {
      var left = (c.start / duration) * 100;
      var width = ((Math.min(c.end, duration) - c.start) / duration) * 100;
      return {
        index: i,
        title: c.title,
        left: Math.max(0, Math.min(100, left)),
        width: Math.max(0, Math.min(100 - left, width))
      };
    });
  }

  /** How far through the current chapter, 0..1 — drives the segment fill. */
  function progressWithin(chapters, t) {
    var idx = indexAt(chapters, t);
    if (idx === -1) return 0;
    var c = chapters[idx];
    var span = c.end - c.start;
    if (span <= 0) return 0;
    return Math.max(0, Math.min(1, (t - c.start) / span));
  }

  function formatTime(seconds) {
    if (!isFinite(seconds) || seconds < 0) seconds = 0;
    var m = Math.floor(seconds / 60);
    var s = Math.floor(seconds % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  global.Chapters = {
    normalize: normalize,
    indexAt: indexAt,
    nextStart: nextStart,
    previousStart: previousStart,
    segments: segments,
    progressWithin: progressWithin,
    formatTime: formatTime
  };
})(typeof window !== 'undefined' ? window : globalThis);
