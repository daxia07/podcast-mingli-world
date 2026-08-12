// Tests for functions/episodes/[file].js — Range handling.
//
// The function is ESM (Pages Functions always are) but the repo's package.json
// has no "type", so Node would read a .js import as CommonJS. Importing the
// source through a data: URL sidesteps that without changing package config.

import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import test from 'node:test';
import assert from 'node:assert/strict';

const here = dirname(fileURLToPath(import.meta.url));
const src = await readFile(join(here, '..', 'functions', 'episodes', '[file].js'), 'utf8');
const mod = await import(
  'data:text/javascript;base64,' + Buffer.from(src).toString('base64')
);
const { parseRange, classifyRange, onRequest } = mod;

// --- parseRange ----------------------------------------------------------

test('parseRange: open-ended range', () => {
  assert.deepEqual(parseRange('bytes=100-', 1000), { offset: 100, length: 900 });
});

test('parseRange: closed range', () => {
  assert.deepEqual(parseRange('bytes=0-99', 1000), { offset: 0, length: 100 });
});

test('parseRange: end past EOF clamps to the last byte', () => {
  assert.deepEqual(parseRange('bytes=900-99999', 1000), { offset: 900, length: 100 });
});

test('parseRange: suffix range returns the final N bytes', () => {
  assert.deepEqual(parseRange('bytes=-500', 1000), { offset: 500, length: 500 });
});

test('parseRange: suffix longer than the object yields the whole object', () => {
  assert.deepEqual(parseRange('bytes=-5000', 1000), { offset: 0, length: 1000 });
});

test('parseRange: start at or past EOF is unsatisfiable', () => {
  assert.equal(parseRange('bytes=1000-', 1000), null);
  assert.equal(parseRange('bytes=2000-3000', 1000), null);
});

test('parseRange: inverted range is rejected', () => {
  assert.equal(parseRange('bytes=500-100', 1000), null);
});

test('classifyRange: separates ignorable from unsatisfiable', () => {
  // RFC 9110: invalid -> ignore (200); past EOF -> 416.
  assert.equal(classifyRange('bytes=500-100', 1000), 'ignore');
  assert.equal(classifyRange('bytes=0-99,200-299', 1000), 'ignore');
  assert.equal(classifyRange('items=0-99', 1000), 'ignore');
  assert.equal(classifyRange('bytes=1000-', 1000), 'unsatisfiable');
  assert.equal(classifyRange(null, 1000), 'none');
});

test('parseRange: multi-range and other units fall back to the whole body', () => {
  assert.equal(parseRange('bytes=0-99,200-299', 1000), null);
  assert.equal(parseRange('items=0-99', 1000), null);
  assert.equal(parseRange(null, 1000), null);
});

// --- onRequest -----------------------------------------------------------

const SIZE = 10_000;

function fakeBucket({ exists = true } = {}) {
  const meta = { size: SIZE, httpEtag: '"abc123"' };
  return {
    calls: [],
    async head(key) {
      this.calls.push(['head', key]);
      return exists ? meta : null;
    },
    async get(key, opts) {
      this.calls.push(['get', key, opts?.range ?? null]);
      if (!exists) return null;
      return { ...meta, body: 'BODY' };
    },
  };
}

function call(bucket, { method = 'GET', range = null, file = 'ep01.mp3' } = {}) {
  const headers = range ? { Range: range } : {};
  return onRequest({
    env: { FEEDBACK_BUCKET: bucket },
    params: { file },
    request: new Request(`https://example.com/episodes/${file}`, { method, headers }),
  });
}

test('GET without Range returns 200 and revalidates', async () => {
  const bucket = fakeBucket();
  const res = await call(bucket);
  assert.equal(res.status, 200);
  assert.equal(res.headers.get('Accept-Ranges'), 'bytes');
  assert.equal(res.headers.get('Cache-Control'), 'public, max-age=3600, must-revalidate');
  assert.equal(res.headers.get('ETag'), '"abc123"');
  // No wasted head() call on the common path.
  assert.deepEqual(bucket.calls, [['get', 'episodes/ep01.mp3', null]]);
});

test('GET with Range returns 206 with a correct Content-Range', async () => {
  const bucket = fakeBucket();
  const res = await call(bucket, { range: 'bytes=1000-1100' });
  assert.equal(res.status, 206);
  assert.equal(res.headers.get('Content-Range'), `bytes 1000-1100/${SIZE}`);
  assert.equal(res.headers.get('Content-Length'), '101');
  // The range must reach R2 — not be silently dropped, which was the bug.
  assert.deepEqual(bucket.calls.at(-1), [
    'get',
    'episodes/ep01.mp3',
    { offset: 1000, length: 101 },
  ]);
});

test('GET with an open-ended Range streams to EOF', async () => {
  const bucket = fakeBucket();
  const res = await call(bucket, { range: 'bytes=9000-' });
  assert.equal(res.status, 206);
  assert.equal(res.headers.get('Content-Range'), `bytes 9000-9999/${SIZE}`);
  assert.equal(res.headers.get('Content-Length'), '1000');
});

test('unsatisfiable Range returns 416 with the object size', async () => {
  const bucket = fakeBucket();
  const res = await call(bucket, { range: 'bytes=99999-' });
  assert.equal(res.status, 416);
  assert.equal(res.headers.get('Content-Range'), `bytes */${SIZE}`);
});

test('malformed Range falls back to the whole body', async () => {
  const bucket = fakeBucket();
  const res = await call(bucket, { range: 'bytes=0-99,200-299' });
  assert.equal(res.status, 200);
});

test('HEAD returns metadata without fetching the body', async () => {
  const bucket = fakeBucket();
  const res = await call(bucket, { method: 'HEAD' });
  assert.equal(res.status, 200);
  assert.equal(res.headers.get('Content-Length'), String(SIZE));
  assert.deepEqual(bucket.calls, [['head', 'episodes/ep01.mp3']]);
});

test('missing object returns 404', async () => {
  const res = await call(fakeBucket({ exists: false }));
  assert.equal(res.status, 404);
});
