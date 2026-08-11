// Tests for site/js/vtt.js and site/js/chapters.js.
//
// Both are classic scripts that attach to a global (the site has no build
// step). They're loaded here by evaluating them against a fake global, which
// is exactly how the browser sees them.

import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));

async function loadGlobals(...files) {
  const sandbox = { window: {} };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  for (const file of files) {
    const src = await readFile(join(here, '..', 'site', 'js', file), 'utf8');
    vm.runInContext(src, sandbox);
  }
  return sandbox.window;
}

const { VTT, Chapters } = await loadGlobals('vtt.js', 'chapters.js');

// --- VTT -----------------------------------------------------------------

const SAMPLE = `WEBVTT

1
00:00:00.000 --> 00:00:04.500
Alright. Interviewer just said: Two Sum.

2
00:00:04.500 --> 00:00:09.000
<v Interviewer>Tell me how you would start.

3
00:00:09.000 --> 00:00:12.250
<v Candidate>I would restate the problem first.
`;

test('parses cues with timings', () => {
  const cues = VTT.parse(SAMPLE);
  assert.equal(cues.length, 3);
  assert.equal(cues[0].start, 0);
  assert.equal(cues[0].end, 4.5);
  assert.equal(cues[0].text, 'Alright. Interviewer just said: Two Sum.');
});

test('extracts speaker tags and strips markup', () => {
  const cues = VTT.parse(SAMPLE);
  assert.equal(cues[1].speaker, 'Interviewer');
  assert.equal(cues[1].text, 'Tell me how you would start.');
  assert.equal(cues[2].speaker, 'Candidate');
});

test('ignores NOTE and STYLE blocks', () => {
  const cues = VTT.parse('WEBVTT\n\nNOTE something\n\nSTYLE\n::cue { color: red }\n\n1\n00:00:01.000 --> 00:00:02.000\nHello\n');
  assert.equal(cues.length, 1);
  assert.equal(cues[0].text, 'Hello');
});

test('handles MM:SS timestamps without an hour field', () => {
  assert.equal(VTT.parseTimestamp('01:02.500'), 62.5);
  assert.equal(VTT.parseTimestamp('00:01:02.500'), 62.5);
});

test('activeIndex finds the cue covering a time', () => {
  const cues = VTT.parse(SAMPLE);
  assert.equal(VTT.activeIndex(cues, 0), 0);
  assert.equal(VTT.activeIndex(cues, 4.4), 0);
  assert.equal(VTT.activeIndex(cues, 4.6), 1);
  assert.equal(VTT.activeIndex(cues, 11), 2);
});

test('activeIndex returns -1 before the first cue and past the last', () => {
  const cues = VTT.parse('WEBVTT\n\n1\n00:00:05.000 --> 00:00:06.000\nHi\n');
  assert.equal(VTT.activeIndex(cues, 1), -1);
  assert.equal(VTT.activeIndex(cues, 99), -1);
  assert.equal(VTT.activeIndex([], 5), -1);
});

test('search returns matching cue indices', () => {
  const cues = VTT.parse(SAMPLE);
  assert.equal(VTT.search(cues, 'restate').join(), '2');
  assert.equal(VTT.search(cues, 'TWO SUM').join(), '0');
  assert.equal(VTT.search(cues, '').length, 0);
});

// --- Chapters ------------------------------------------------------------

const DOC = {
  version: '1.2.0',
  chapters: [
    { startTime: 0, endTime: 60, title: 'Cold open' },
    { startTime: 60, endTime: 180, title: 'Clarify first' },
    { startTime: 180, endTime: 300, title: 'Naive approach' }
  ]
};

test('normalize sorts and fills missing end times', () => {
  const list = Chapters.normalize(
    { chapters: [{ startTime: 100, title: 'B' }, { startTime: 0, title: 'A' }] },
    240
  );
  assert.equal(list.map((c) => c.title).join(), 'A,B');
  assert.equal(list[0].end, 100);
  assert.equal(list[1].end, 240);
});

test('indexAt locates the chapter for a position', () => {
  const list = Chapters.normalize(DOC, 300);
  assert.equal(Chapters.indexAt(list, 0), 0);
  assert.equal(Chapters.indexAt(list, 59.9), 0);
  assert.equal(Chapters.indexAt(list, 60), 1);
  assert.equal(Chapters.indexAt(list, 299), 2);
  assert.equal(Chapters.indexAt(list, 300), 2);
});

test('nextStart skips to the following chapter', () => {
  const list = Chapters.normalize(DOC, 300);
  assert.equal(Chapters.nextStart(list, 0), 60);
  assert.equal(Chapters.nextStart(list, 61), 180);
  assert.equal(Chapters.nextStart(list, 250), null);
});

test('previousStart restarts the chapter, then steps back', () => {
  const list = Chapters.normalize(DOC, 300);
  // Well into chapter 2 -> back to its own start.
  assert.equal(Chapters.previousStart(list, 120), 60);
  // Just after the boundary -> the previous chapter.
  assert.equal(Chapters.previousStart(list, 61), 0);
  assert.equal(Chapters.previousStart(list, 5), 0);
});

test('segments produce non-overlapping percentage geometry', () => {
  const segs = Chapters.segments(Chapters.normalize(DOC, 300), 300);
  assert.equal(segs.length, 3);
  assert.equal(segs[0].left, 0);
  assert.equal(segs[0].width, 20);
  assert.equal(segs[1].left, 20);
  assert.equal(segs[2].left + segs[2].width, 100);
  for (const s of segs) {
    assert.ok(s.left >= 0 && s.left + s.width <= 100.0001, 'segment stays in bounds');
  }
});

test('progressWithin measures position inside the current chapter', () => {
  const list = Chapters.normalize(DOC, 300);
  assert.equal(Chapters.progressWithin(list, 0), 0);
  assert.equal(Chapters.progressWithin(list, 30), 0.5);
  assert.equal(Chapters.progressWithin(list, 120), 0.5);
});

test('empty or absent chapter data degrades quietly', () => {
  // Arrays cross a vm realm boundary here, so compare length not identity.
  assert.equal(Chapters.normalize(null, 100).length, 0);
  assert.equal(Chapters.segments([], 100).length, 0);
  assert.equal(Chapters.indexAt([], 5), -1);
  assert.equal(Chapters.progressWithin([], 5), 0);
});

test('formatTime', () => {
  assert.equal(Chapters.formatTime(0), '0:00');
  assert.equal(Chapters.formatTime(65), '1:05');
  assert.equal(Chapters.formatTime(NaN), '0:00');
});
