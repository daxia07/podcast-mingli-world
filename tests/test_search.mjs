// Tests for site/js/search.js — ranking, moment lookup and snippeting.
//
// The interesting cases are the ones that are tedious to check on a phone: that
// a term only ever *spoken* still finds its episode, that AND across terms is
// honoured across both corpora, and that highlighting survives overlapping
// matches without duplicating text.

import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));

async function load() {
  const sandbox = { window: {} };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  const src = await readFile(join(here, '..', 'site', 'js', 'search.js'), 'utf8');
  vm.runInContext(src, sandbox);
  return sandbox.window.Search;
}

// Values built inside the vm come from another realm, so deepEqual compares
// their prototypes and fails on structurally identical objects. Round-tripping
// through JSON brings them home.
const plain = (v) => JSON.parse(JSON.stringify(v));

const EPISODES = [
  { id: 1, title: 'Vector Databases Explained', playlist: 'system-design', date: '2026-01-02' },
  { id: 2, title: 'Rate Limiting', description: 'Token bucket and leaky bucket.', playlist: 'system-design', date: '2026-01-03' },
  { id: 3, title: 'Responsible AI', playlist: 'aws-ai-practitioner', date: '2026-01-04' },
];

// Episode 3 never says "vector" in its metadata — only in the audio.
const INDEX = {
  version: 1,
  episodes: {
    3: {
      s: 'responsible-ai',
      c: [[0, 'Bias and fairness'], [120, 'Vector stores and guardrails']],
      l: [
        [12.5, 'Fairness metrics matter when a model decides who gets a loan.'],
        [130.2, 'A vector database is how retrieval augmented generation finds context.'],
        [190.0, 'Short line.'],
      ],
    },
  },
};

const CTX = { episodes: EPISODES, index: INDEX, solutions: {}, showTitle: () => 'A Show' };

// --- terms ----------------------------------------------------------------

test('terms splits on whitespace and drops one-character noise', async () => {
  const S = await load();
  assert.deepEqual(plain(S.terms('  Vector   a DB ')), ['vector', 'db']);
});

test('quoted phrases stay one term', async () => {
  const S = await load();
  assert.deepEqual(plain(S.terms('"vector database" rag')), ['vector database', 'rag']);
});

test('an empty query yields no terms and no results', async () => {
  const S = await load();
  assert.deepEqual(plain(S.terms('   ')), []);
  assert.deepEqual(plain(S.run('   ', CTX)), []);
});

// --- matching -------------------------------------------------------------

test('a title match ranks above a spoken-only match', async () => {
  const S = await load();
  const out = S.run('vector', CTX);
  assert.equal(out[0].ep.id, 1, 'the episode named Vector Databases comes first');
  assert.ok(out.some((r) => r.ep.id === 3), 'the episode that only says it is still found');
});

test('an episode found only through its transcript carries its moments', async () => {
  const S = await load();
  const hit = S.run('retrieval augmented', CTX).find((r) => r.ep.id === 3);
  assert.ok(hit, 'found via spoken text alone');
  assert.equal(hit.moments.length, 1);
  assert.equal(hit.moments[0].t, 130.2);
  assert.equal(hit.moments[0].kind, 'line');
});

test('AND across terms may be satisfied by metadata and audio together', async () => {
  const S = await load();
  // "responsible" is in the title, "guardrails" only in a chapter.
  const out = S.run('responsible guardrails', CTX);
  assert.equal(out.length, 1);
  assert.equal(out[0].ep.id, 3);
});

test('a term nothing matches removes the episode entirely', async () => {
  const S = await load();
  assert.deepEqual(plain(S.run('vector kubernetes', CTX)), []);
});

test('the solution board is searchable', async () => {
  const S = await load();
  const ctx = {
    ...CTX,
    solutions: { 2: { title: 'Rate limit', problem: 'Design a throttle', sections: [{ title: 'Sliding window', body: ['Use a redis sorted set.'] }] } },
  };
  const out = S.run('redis', ctx);
  assert.equal(out.length, 1);
  assert.equal(out[0].ep.id, 2);
});

// --- moments --------------------------------------------------------------

test('a chapter outranks a line when both match once', async () => {
  const S = await load();
  const found = S.momentsFor(INDEX.episodes[3], ['vector']);
  assert.equal(found[0].kind, 'chapter');
  assert.equal(found[0].t, 120);
});

test('moments are capped and ordered by time within a score', async () => {
  const S = await load();
  const entry = { l: [[30, 'alpha here'], [10, 'alpha there'], [20, 'alpha everywhere']] };
  const found = S.momentsFor(entry, ['alpha']);
  assert.deepEqual(plain(found).map((m) => m.t), [10, 20, 30]);
});

test('momentsFor on a missing entry is empty, not a throw', async () => {
  const S = await load();
  assert.deepEqual(plain(S.momentsFor(undefined, ['x'])), []);
});

// --- presentation ---------------------------------------------------------

test('highlight marks every occurrence and loses no text', async () => {
  const S = await load();
  const chunks = S.highlight('Vector maths and vector stores', ['vector']);
  assert.equal(chunks.map((c) => c.t).join(''), 'Vector maths and vector stores');
  assert.equal(chunks.filter((c) => c.hit).length, 2);
  assert.equal(chunks[0].t, 'Vector', 'case is preserved from the source');
});

test('overlapping terms merge into one mark rather than duplicating text', async () => {
  const S = await load();
  const chunks = S.highlight('a vector database here', ['vector', 'vector data']);
  assert.equal(chunks.map((c) => c.t).join(''), 'a vector database here');
  assert.equal(chunks.filter((c) => c.hit).length, 1);
});

test('highlight with no match returns the text untouched', async () => {
  const S = await load();
  assert.deepEqual(plain(S.highlight('nothing here', ['zzz'])), [{ t: 'nothing here', hit: false }]);
});

test('a long line is windowed around the match', async () => {
  const S = await load();
  const long = 'x'.repeat(300) + ' needle ' + 'y'.repeat(300);
  const out = S.snippet(long, ['needle']);
  assert.ok(out.includes('needle'));
  assert.ok(out.length < long.length / 2);
  assert.ok(out.startsWith('…') && out.endsWith('…'));
});

test('a short line is returned whole, without ellipses', async () => {
  const S = await load();
  assert.equal(S.snippet('Short and sweet needle.', ['needle']), 'Short and sweet needle.');
});
